# MeshMind Source of Truth

This document describes the current structure, components, and data flow of the MeshMind codebase. It is intended to help new contributors understand how the pieces fit together and where to extend the system.

## Repository Layout

```
meshmind/
├── api/                # MemoryManager CRUD adapter
├── cli/                # Command line entry points (meshmind ingest)
├── client.py           # High-level MeshMind façade
├── core/               # Config, embeddings, similarity, types, utilities
├── db/                 # Graph driver abstractions (Memgraph)
├── models/             # Registry helpers for entities/predicates (unused)
├── pipeline/           # Extraction, preprocessing, storage, maintenance steps
├── retrieval/          # In-memory search strategies and filters
├── tasks/              # Celery app bootstrap and scheduled jobs
├── tests/              # Pytest suites (require monkeypatching)
└── examples/           # Extraction/preprocess/store example script & notebook
```

Supporting files include `README.md` (legacy), `NEW_README.md` (current state), `pyproject.toml` (packaging), `Makefile` (dev commands), and `docker-compose.yml` (placeholder; not wired to services).

## Configuration (`meshmind/core/config.py`)

- Reads environment variables for Memgraph (`MEMGRAPH_URI`, `MEMGRAPH_USERNAME`, `MEMGRAPH_PASSWORD`), Redis (`REDIS_URL`), OpenAI API key, and default embedding model name (`EMBEDDING_MODEL`).
- Uses `python-dotenv` if available to load a `.env` file.
- Exposes a singleton `settings` object consumed throughout the codebase.

## Data Models (`meshmind/core/types.py`)

- `Memory`: Pydantic model with fields `uuid`, `namespace`, `name`, `entity_label`, optional `embedding`, arbitrary `metadata`, timestamps (`created_at`, `updated_at`), `importance`, `ttl_seconds`, and optional `reference_time`.
- `Triplet`: Represents a subject–predicate–object relation (currently unused by the pipeline).
- `SearchConfig`: Configures retrieval (`encoder`, `top_k`, `rerank_k`, `filters`, `hybrid_weights`).

## Client (`meshmind/client.py`)

- `MeshMind` constructor wires up:
  - `self.llm_client`: `openai.OpenAI()` instance unless supplied.
  - `self.embedding_model`: from settings or override.
  - `self.driver`: `MemgraphDriver(settings.MEMGRAPH_URI, ...)` unless a custom driver is injected.
- Exposes thin wrappers that delegate to pipeline modules:
  - `extract_memories` → `meshmind.pipeline.extract.extract_memories`
  - `deduplicate`, `score_importance`, `compress` → `meshmind.pipeline.preprocess`
  - `store_memories` → `meshmind.pipeline.store.store_memories`
- **Important**: No higher-level APIs (registering entities/predicates, storing triplets) exist yet.

## Pipeline Modules (`meshmind/pipeline/`)

1. **Extraction (`extract.py`)**
   - Builds an OpenAI Responses API call with function-calling against the `Memory` JSON schema.
   - Requires a list of allowed entity types (only the class names are checked) and a registered embedding encoder.
   - Post-processes the function-call output, injects the namespace, validates via `Memory(**entry)`, and populates embeddings.

2. **Preprocessing (`preprocess.py`)**
   - `deduplicate`: Removes duplicates by exact name match and, when `threshold >= 0.5`, by cosine similarity over embeddings.
   - `score_importance`: Sets missing importance scores to `1.0`.
   - `compress`: Delegates to `compress_memories`; catches `ImportError` and generic exceptions to fall back to original memories.

3. **Compression (`compress.py`)**
   - Uses `tiktoken` to truncate memory `metadata['content']` to `max_tokens` (default 500). Requires `tiktoken.get_encoding('o200k_base')`.

4. **Consolidation (`consolidate.py`)**
   - Groups memories by name and retains the one with the highest `importance` (ties fall back to first seen).

5. **Expiry (`expire.py`)**
   - Iterates `MemoryManager.list_memories()`, compares `created_at + ttl_seconds` with `datetime.utcnow()`, and calls `delete_memory` for expired entries.

6. **Store (`store.py`)**
   - Iterates an iterable of memories, extracts their dict representation, and invokes `GraphDriver.upsert_entity`. Relationships are not handled.

## Graph Layer (`meshmind/db/`)

- `base_driver.py`: Defines the `GraphDriver` abstract base class (`upsert_entity`, `upsert_edge`, `find`, `delete`).
- `memgraph_driver.py`:
  - Imports `mgclient` and connects to Memgraph via Bolt using the configured URI.
  - Implements `upsert_entity` (MERGE on `uuid`), `upsert_edge` (MERGE between nodes identified by UUID), `find` (executes arbitrary Cypher and returns list of dicts), `delete` (DETACH DELETE by uuid), and `vector_search` (loads all embeddings and ranks via cosine similarity in Python).
  - Raises `ImportError` at instantiation time when `mgclient` is missing.

## Embeddings & Similarity (`meshmind/core/embeddings.py`, `similarity.py`)

- `EncoderRegistry`: simple class-level registry mapping string names to encoder instances (`register`, `get`). Nothing is pre-registered.
- `OpenAIEmbeddingEncoder`: wraps the OpenAI Embeddings API with retries; assumes dictionary-style responses (`response['data']`).
- `SentenceTransformerEncoder`: wraps `sentence-transformers` for local embeddings.
- `similarity.py`: provides `cosine_similarity` and `euclidean_distance` utilities using NumPy.

## Retrieval (`meshmind/retrieval/`)

- `filters.py`: filter helpers by namespace, entity labels, and metadata exact matches.
- `bm25.py`: TF-IDF vectorizer + cosine similarity to approximate BM25 scoring.
- `fuzzy.py`: RapidFuzz-based WRatio scoring.
- `hybrid.py`: Computes query embeddings via a registered encoder, fuses with BM25 scores using weights in `SearchConfig`, and returns ranked tuples.
- `search.py`: Dispatcher functions `search` (hybrid with filters), `search_bm25`, and `search_fuzzy`.
- **Limitation**: All retrieval operates on in-memory lists supplied by the caller; there is no integration with the graph driver.

## CLI (`meshmind/cli/`)

- `__main__.py`: CLI bootstrap with `ingest` subcommand.
- `ingest.py`: Walks provided paths, reads text files, runs extraction/preprocessing/store via `MeshMind`. Uses `entity_types=[Memory]` by default.

## Tasks (`meshmind/tasks/`)

- `celery_app.py`: Creates a Celery app configured with Redis if `celery` is installed; otherwise provides a no-op dummy app.
- `scheduled.py`:
  - Attempts to instantiate `MemgraphDriver` and `MemoryManager` at import time; on failure sets them to `None`.
  - Configures Celery beat schedules for expiry (daily), consolidation (every 6 hours), and compression (every 12 hours).
  - Defines tasks `expire_task`, `consolidate_task`, and `compress_task` that operate on `manager` if available, else return immediately.

## API Layer (`meshmind/api/memory_manager.py`)

- Provides CRUD-style methods `add_memory`, `update_memory`, `delete_memory`, `get_memory`, and `list_memories` by delegating to the injected `GraphDriver`.
- Converts Pydantic models to dicts via `memory.dict(exclude_none=True)` when possible.

## Models (`meshmind/models/registry.py`)

- Defines `EntityRegistry` and `PredicateRegistry` for registering Pydantic models and allowed predicate labels.
- Currently unused by the rest of the system.

## Examples & Tests

- `examples/extract_preprocess_store_example.py`: Demonstrates extraction, preprocessing, and storage using the CLI components.
- `meshmind/tests`: Contains pytest modules covering extraction, preprocessing, driver behavior, retrieval, similarity, and maintenance tasks. Many tests rely on dummy dependencies or outdated OpenAI interfaces; the suite requires extensive monkeypatching to run.

## External Dependencies

- **Memgraph + mgclient**: Required for `MemgraphDriver`. Without mgclient, most functionality that instantiates `MeshMind` will fail.
- **OpenAI SDK**: Used for extraction (Responses API) and embeddings.
- **tiktoken**: Needed for compression utilities and token counting (also imported by `meshmind.core.utils`).
- **RapidFuzz, scikit-learn, numpy**: Power the retrieval modules.
- **Celery + Redis**: Optional, used only if scheduled maintenance tasks are activated.
- **sentence-transformers**: Optional embedding encoder.

## Known Gaps & Caveats

- No default encoder registration; consumers must call `EncoderRegistry.register` before invoking extraction or hybrid search.
- Relationship storage (`Triplet`, predicate registry) is unimplemented; only nodes are persisted.
- Driver initialization is eager and fails without Memgraph/mgclient.
- Optional dependencies are not guarded consistently, leading to import-time crashes when missing.
- Tests require updates to match current library behavior and to run without external services.

Maintain this document as the system evolves to keep onboarding friction low.
