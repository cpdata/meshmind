# MeshMind Source of Truth

This document summarizes the current architecture, supporting assets, and operational expectations for MeshMind. Update it
whenever workflows or modules change so new contributors can find accurate information in one place.

## Repository Layout
```
meshmind/
├── api/                # MemoryManager CRUD adapter that wraps a GraphDriver
├── cli/                # CLI entry point and ingest command
├── client.py           # High-level MeshMind façade and orchestration helpers
├── core/               # Configuration, embeddings, types, similarity, shared utilities
├── db/                 # Graph driver abstractions plus Memgraph implementation
├── models/             # Entity and predicate registries shared across the pipeline
├── pipeline/           # Extract, preprocess, compression, storage, consolidation, expiry stages
├── retrieval/          # Search strategies (hybrid, lexical, fuzzy, vector, regex, rerank helpers)
├── tasks/              # Celery beat schedules and maintenance jobs
├── tests/              # Pytest suites with local fixtures (no external services required)
└── examples/           # Scripts and notebooks showing ingestion and retrieval flows
```
Supporting assets:
- `Makefile`: Development automation (linting, formatting, type checks, tests, docker compose).
- `.github/workflows/ci.yml`: GitHub Actions workflow running linting/formatting checks and pytest.
- `pyproject.toml`: Project metadata and dependency list (targets Python 3.13, see blockers in `ISSUES.md`).
- Documentation (`PROJECT.md`, `PLAN.md`, `SOT.md`, `README_LATEST.md`, etc.) describing the system and roadmap.

## Configuration (`meshmind/core/config.py`)
- Loads environment variables for Memgraph (`MEMGRAPH_URI`, `MEMGRAPH_USERNAME`, `MEMGRAPH_PASSWORD`), Redis
  (`REDIS_URL`), OpenAI (`OPENAI_API_KEY`), and the default embedding model (`EMBEDDING_MODEL`).
- Uses `python-dotenv` when available to hydrate values from a `.env` file automatically.
- Provides a module-level `settings` instance used across the client, drivers, CLI, and Celery tasks.

## Core Data Models (`meshmind/core/types.py`)
- `Memory`: Pydantic model that represents a knowledge record, including embeddings, metadata, and optional TTL.
- `Triplet`: Subject–predicate–object edge connecting two memory UUIDs with namespace and metadata.
- `SearchConfig`: Retrieval configuration (encoder name, `top_k`, `rerank_k`, optional rerank model, metadata filters,
  hybrid weights).

## Client (`meshmind/client.py`)
- `MeshMind` bootstraps:
  - Default OpenAI client (Responses API) when the SDK is installed; custom clients can be injected for testing.
  - Embedding model from configuration with encoder bootstrap that registers available adapters.
  - Graph driver factory that creates a `MemgraphDriver` lazily only when persistence is required.
- Provides convenience helpers:
  - Pipelines: `extract_memories`, `deduplicate`, `score_importance`, `compress`, `store_memories`, `store_triplets`.
  - CRUD: `create_memory`, `update_memory`, `delete_memory`, `get_memory`, `list_memories`, `list_triplets`.
  - Retrieval: `search` (hybrid + optional LLM rerank), `search_vector`, `search_regex`, `search_exact`.
- Exposes `graph_driver`/`driver` properties that surface the active graph driver instance on demand.

## Embeddings & Utilities (`meshmind/core/embeddings.py`, `meshmind/core/utils.py`)
- `EncoderRegistry` manages encoder instances (OpenAI embeddings, sentence-transformers, custom fixtures).
- OpenAI and SentenceTransformer adapters provide encoding with retry logic and optional fallbacks.
- Utility functions provide UUIDs, timestamps, hashing, and token counting guarded behind optional `tiktoken` imports.

## Database Layer (`meshmind/db`)
- `GraphDriver` defines the persistence contract (entity upserts, relationship upserts, querying, deletions, triplet listing).
- `MemgraphDriver` wraps `mgclient`, handles URI parsing, executes Cypher statements, and exposes a Python-side vector search
  fallback when database-native similarity is unavailable.

## Pipeline Modules (`meshmind/pipeline`)
1. **Extraction (`extract.py`)** – Orchestrates OpenAI function calling against the `Memory` schema, enforces entity label filters,
   and populates embeddings via registered encoders.
2. **Preprocess (`preprocess.py`)** – Deduplicates by name/embedding similarity, ensures memories have importance scores, and
   delegates to compression when available.
3. **Compress (`compress.py`)** – Truncates metadata payloads to configurable token budgets when `tiktoken` is installed.
4. **Store (`store.py`)** – Persists memories and triplets using the configured `GraphDriver`, registering predicates as needed.
5. **Consolidate & Expire (`consolidate.py`, `expire.py`)** – Maintenance utilities triggered by Celery tasks to group memories
   and remove stale entries.

## Retrieval (`meshmind/retrieval`)
- `filters.py`: Namespace, entity label, and metadata filtering helpers.
- `bm25.py`, `fuzzy.py`: Lexical and fuzzy scorers using scikit-learn TF-IDF + cosine and RapidFuzz WRatio respectively.
- `vector.py`: Vector-only search utilities with cosine similarity and optional precomputed query embeddings.
- `hybrid.py`: Combines vector and BM25 scores with configurable weights defined in `SearchConfig`.
- `search.py`: Dispatchers for hybrid, BM25, fuzzy, vector, regex, and exact-match search modes plus metadata filters.
- `rerank.py`: Generic reranker interface and LLM-based rerank helper compatible with the OpenAI Responses API.

## CLI (`meshmind/cli`)
- `meshmind.cli.__main__`: Entry point exposing an `ingest` command for local pipelines.
- CLI bootstraps encoder and entity registries, validates configuration early, and surfaces actionable errors when optional
  dependencies are missing.

## Tasks (`meshmind/tasks`)
- `celery_app.py`: Creates the Celery application lazily, returning a shim when Celery is not installed.
- `scheduled.py`: Defines periodic consolidation, compression, and expiry jobs that now initialize drivers and managers lazily
  to tolerate missing dependencies during import.

## API Adapter (`meshmind/api/memory_manager.py`)
- Manages CRUD operations against the graph driver, including triplet persistence and deletion helpers.
- Returns Pydantic models for list/get operations and gracefully handles missing records.

## Models (`meshmind/models/registry.py`)
- `EntityRegistry` and `PredicateRegistry` store class metadata and permitted predicates.
- Registries are populated during bootstrap and extended as new entity/predicate types are defined.

## Examples & Tests
- `examples/extract_preprocess_store_example.py`: Demonstrates extraction, preprocessing, triplet creation, and multiple
  retrieval strategies.
- `meshmind/tests`: Pytest suites rely on fixtures (`memory_factory`, `dummy_encoder`) and pure-Python stubs, allowing the
  suite to run without Memgraph, OpenAI, or Redis dependencies.

## External Dependencies
- Required: `openai`, `pydantic`, `pydantic-settings`, `numpy`, `scikit-learn`, `rapidfuzz`, `python-dotenv`, `pymgclient`.
- Optional but supported: `tiktoken`, `sentence-transformers`, `celery[redis]`, `typeguard`, `pyright`, `toml-sort`, `yamllint`.
- Development tooling introduced in the Makefile/CI expects `ruff`, `pyright`, `typeguard`, `toml-sort`, and `yamllint`.

## Operational Notes
- Graph persistence requires a running Memgraph instance reachable via `settings.MEMGRAPH_URI` and `pymgclient` installed.
- Encoder registration occurs during bootstrap; ensure at least one embedding encoder is available before extraction/search.
- LLM reranking uses the OpenAI Responses API. Provide `OPENAI_API_KEY` and confirm the selected `SearchConfig.rerank_model` is
  deployed to your account.
- Local development commands rely on external tooling (ruff, pyright, typeguard, toml-sort, yamllint); install them via the
  Makefile or the CI workflow instructions in `README_LATEST.md`.
