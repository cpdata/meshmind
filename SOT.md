# MeshMind Source of Truth

This document captures the current architecture, modules, and operational expectations for MeshMind. Update it whenever code structure or workflows change so new contributors can ramp up quickly.

## Repository Layout
```
meshmind/
├── api/                # MemoryManager CRUD adapter
├── cli/                # CLI entry point and ingest command
├── client.py           # High-level MeshMind façade
├── core/               # Config, types, embeddings, similarity, utilities
├── db/                 # Graph driver abstractions (Memgraph)
├── models/             # Entity/predicate registries (not yet integrated)
├── pipeline/           # Extraction, preprocessing, storage, maintenance steps
├── retrieval/          # In-memory search strategies and filters
├── tasks/              # Celery wiring and scheduled jobs
├── tests/              # Pytest suites (require extensive monkeypatching)
└── examples/           # Example extraction/preprocess/store script
```
Supporting files include:
- `pyproject.toml`: project metadata (declares Python >=3.13, which is aspirational).
- `docker-compose.yml`: placeholder with no services defined.
- `Makefile`: minimal development targets (currently none for testing).
- Documentation artifacts (`PROJECT.md`, `PLAN.md`, etc.).

## Configuration (`meshmind/core/config.py`)
- Loads environment variables for Memgraph (`MEMGRAPH_URI`, `MEMGRAPH_USERNAME`, `MEMGRAPH_PASSWORD`), Redis (`REDIS_URL`), OpenAI (`OPENAI_API_KEY`), and default embedding model (`EMBEDDING_MODEL`).
- Uses `python-dotenv` if available to load `.env` files at import time.
- Exposes a module-level `settings` object consumed by clients, drivers, and tasks.

## Core Data Models (`meshmind/core/types.py`)
- `Memory`: Pydantic model representing a knowledge record. Fields include `uuid`, `namespace`, `name`, `entity_label`, optional `embedding`, `metadata`, `reference_time`, `created_at`, `updated_at`, `importance`, and `ttl_seconds`.
- `Triplet`: Subject–predicate–object relationship with namespace, entity label, metadata, and optional reference time. Not used in current flows.
- `SearchConfig`: Retrieval configuration (encoder name, `top_k`, `rerank_k`, metadata filters, hybrid weights).

## Client (`meshmind/client.py`)
- `MeshMind` constructor wires:
  - `OpenAI()` as the default LLM client (fails if OpenAI SDK is missing or API key absent).
  - Embedding model name from `settings.EMBEDDING_MODEL`.
  - `MemgraphDriver` instantiated with configured URI/credentials (raises `ImportError` if `mgclient` is unavailable).
- Provides high-level helpers:
  - `extract_memories` delegates to `pipeline.extract.extract_memories` (requires an encoder in `EncoderRegistry`).
  - `deduplicate`, `score_importance`, `compress` delegate to `pipeline.preprocess`.
  - `store_memories` delegates to `pipeline.store.store_memories`.
- Does **not** expose registration, triplet storage, or CRUD methods promised in the legacy README.

## Embeddings & Utilities (`meshmind/core/embeddings.py`, `meshmind/core/utils.py`)
- `EncoderRegistry`: Class-level map from string key to encoder instance. Call `register(name, encoder)` before extraction or hybrid search.
- `OpenAIEmbeddingEncoder`: Wraps the OpenAI Embeddings API with retry logic but assumes dictionary-style responses (`response['data']`), which is incompatible with current SDK objects.
- `SentenceTransformerEncoder`: Provides local embedding support via `sentence-transformers`.
- `meshmind.core.utils`: Supplies UUID generation, timestamp helpers, hashing, and token counting. Imports `tiktoken` at module load, so missing the package raises immediately.

## Database Layer (`meshmind/db`)
- `base_driver.py`: Abstract `GraphDriver` defining `upsert_entity`, `upsert_edge`, `find`, and `delete` signatures.
- `memgraph_driver.py`:
  - Imports `mgclient` and opens a Bolt connection on instantiation.
  - Implements node upserts (MERGE by `uuid`), edge upserts (MERGE by `uuid`), arbitrary Cypher `find`, deletion, and a naive Python-based vector search over stored embeddings.
  - Requires `mgclient`; otherwise constructing the driver raises `ImportError`.

## Pipeline Modules (`meshmind/pipeline`)
1. **Extraction (`extract.py`)**
   - Builds an OpenAI Responses API call with function-calling against the `Memory` JSON schema.
   - Validates `entity_label` against supplied `entity_types` (string comparison only) and populates embeddings via `EncoderRegistry`.
2. **Preprocess (`preprocess.py`)**
   - `deduplicate`: Removes duplicates by name and optionally by cosine similarity when embeddings exist.
   - `score_importance`: Assigns a default importance of `1.0` when missing.
   - `compress`: Delegates to `pipeline.compress.compress_memories` and falls back on errors.
3. **Compress (`compress.py`)**
   - Uses `tiktoken` to truncate `metadata['content']` to a token budget (requires the package).
4. **Consolidate (`consolidate.py`)**
   - Groups memories by name and selects the highest-importance entry (no persistence built in).
5. **Expire (`expire.py`)**
   - Deletes memories whose `created_at + ttl_seconds` is in the past using `MemoryManager`.
6. **Store (`store.py`)**
   - Iterates memories and calls `GraphDriver.upsert_entity`. Relationships are not touched.

## Retrieval (`meshmind/retrieval`)
- `filters.py`: Filter helpers by namespace, entity labels, and metadata equality.
- `bm25.py`: TF-IDF vectorizer + cosine similarity (scikit-learn) used as a lexical scorer.
- `fuzzy.py`: RapidFuzz WRatio scoring for fuzzy name matching.
- `hybrid.py`: Combines query embeddings (from registered encoder) with BM25 scores using configurable weights.
- `search.py`: Dispatchers for hybrid (`search`), lexical (`search_bm25`), and fuzzy (`search_fuzzy`) retrieval. Operate on caller-provided lists of `Memory` objects; no direct graph querying.

## CLI (`meshmind/cli`)
- `__main__.py`: Defines the `meshmind` CLI with an `ingest` subcommand.
- `ingest.py`: Walks files/directories, reads text contents, runs extraction + preprocessing + storage. Hardcodes `entity_types=[Memory]` and assumes an encoder is already registered.

## Tasks (`meshmind/tasks`)
- `celery_app.py`: Creates a Celery app when the library is installed; otherwise exposes a no-op shim.
- `scheduled.py`:
  - Attempts to instantiate `MemgraphDriver` and `MemoryManager` at import time, falling back to `None` when dependencies fail.
  - Configures Celery beat schedules for expiry (daily), consolidation (every 6 hours), and compression (every 12 hours).
  - Defines tasks that operate on the global `manager` instance; if initialization failed they return empty results.

## API Adapter (`meshmind/api/memory_manager.py`)
- Wraps a graph driver to provide CRUD helpers (`add_memory`, `update_memory`, `delete_memory`, `get_memory`, `list_memories`).
- Converts Pydantic objects to dicts via `memory.dict(exclude_none=True)` with fallback to `__dict__`.
- Currently the primary way to list memories for retrieval; not exposed through the CLI or `MeshMind` convenience methods.

## Models (`meshmind/models/registry.py`)
- `EntityRegistry` and `PredicateRegistry` store registered models and allowed relationship labels.
- No production code writes to these registries yet; integrating them is part of the future roadmap.

## Examples & Tests
- `examples/extract_preprocess_store_example.py`: Demonstrates extraction and storage using `MeshMind`. Requires valid OpenAI credentials and Memgraph.
- Tests under `meshmind/tests` cover extraction, preprocessing, driver behavior, retrieval, similarity, and maintenance tasks. They rely on monkeypatching dummy encoders, OpenAI clients, and mgclient modules. Some tests assume attributes (`Memory.pre_init`) that are not defined in production code, so the suite will fail until updated.

## External Dependencies
- **OpenAI SDK**: Required for extraction and embeddings. Update to latest `openai` package and adjust code accordingly.
- **mgclient**: Required for Memgraph persistence; missing package prevents `MeshMind` construction.
- **tiktoken**: Required for compression and utility token counting. Currently imported eagerly.
- **scikit-learn**, **rapidfuzz**, **numpy**: Support retrieval algorithms.
- **sentence-transformers** (optional): Alternative embedding encoder.
- **celery** and **redis** (optional): Required for scheduled maintenance tasks.

## Operational Caveats
- No encoder is registered by default; failing to register one causes extraction and hybrid search to raise `KeyError`.
- `MeshMind` cannot be instantiated in environments lacking Memgraph or mgclient, limiting portability.
- Relationship data is not persisted, so graph analyses beyond isolated nodes are impossible.
- Tests and CLI commands assume manual setup of encoders and environment variables.
- `docker-compose.yml` does not start required services; developers must provision Memgraph and Redis separately.

## Related Documentation
- `PROJECT.md`: Architectural summary, capability matrix, and roadmap themes.
- `PLAN.md`: Actionable next steps to close gaps.
- `DISCREPANCIES.md`: Detailed comparison between the legacy README and actual implementation.
- `RECOMMENDATIONS.md`: Suggested improvements ranked by impact.
