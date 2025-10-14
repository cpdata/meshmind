# MeshMind Source of Truth

This document summarizes the current architecture, supporting assets, and operational expectations for MeshMind. Update it
whenever workflows or modules change so new contributors can find accurate information in one place.

## Repository Layout
```
meshmind/
├── api/                # MemoryManager CRUD adapter plus REST/gRPC service layers
├── cli/                # CLI entry point, ingest command, and admin utilities
├── client.py           # High-level MeshMind façade and orchestration helpers
├── core/               # Configuration, embeddings, types, similarity, shared utilities
├── db/                 # Graph driver abstractions plus in-memory, SQLite, Memgraph, and Neo4j implementations
├── models/             # Entity and predicate registries shared across the pipeline
├── pipeline/           # Extract, preprocess, compression, storage, consolidation, expiry stages with telemetry hooks
├── retrieval/          # Search strategies (hybrid, lexical, fuzzy, vector, regex, rerank helpers)
├── tasks/              # Celery beat schedules and maintenance jobs
├── testing/            # Fake drivers (Memgraph, Redis, embedding) for offline tests
├── _compat/            # Compatibility shims (e.g., fallback Pydantic base classes)
├── tests/              # Pytest suites with local fixtures (no external services required)
└── examples/           # Scripts and notebooks showing ingestion and retrieval flows
```
Supporting assets:
- `Makefile`: Development automation (linting, formatting, type checks, docs guard, docker compose).
- `docker-compose.yml`: Provisions Memgraph, Neo4j, and Redis for local orchestration; targeted stacks for tests live in
  `meshmind/tests/docker/` (Memgraph-only, Neo4j-only, Redis-only, and full integration).
- `SETUP.md`: End-to-end provisioning instructions covering Python deps, environment variables, and Compose workflows.
- `run/install_setup.sh`, `run/maintenance_setup.sh`: Automation scripts for provisioning fresh environments and refreshing cached workspaces.
- `.github/workflows/ci.yml`: GitHub Actions workflow running linting/formatting checks and pytest.
- `pyproject.toml`: Project metadata and dependency list (pins Python `>=3.11,<3.13`; see compatibility notes in `ISSUES.md`).
- Documentation (`PROJECT.md`, `PLAN.md`, `SOT.md`, `README.md`, etc.) describing the system and roadmap.
- `DUMMIES.md`: Catalog of temporary shims (Pydantic fallback, REST/gRPC stubs, Celery dummies, fake drivers) with removal
  guidance now that dependencies can be installed.

## Configuration (`meshmind/core/config.py`)
- Loads environment variables for the active graph backend (`GRAPH_BACKEND`), Memgraph (`MEMGRAPH_URI`, `MEMGRAPH_USERNAME`,
  `MEMGRAPH_PASSWORD`), SQLite (`SQLITE_PATH`), optional Neo4j (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`), Redis
  (`REDIS_URL`), OpenAI (`OPENAI_API_KEY`), and the default embedding model (`EMBEDDING_MODEL`).
- Uses `python-dotenv` when available to hydrate values from a `.env` file automatically.
- Provides a module-level `settings` instance used across the client, drivers, CLI, and Celery tasks.

## Core Data Models (`meshmind/core/types.py`)
- `Memory`: Pydantic model (or compatibility fallback) that represents a knowledge record, including embeddings, metadata, and optional TTL.
- `Triplet`: Subject–predicate–object edge connecting two memory UUIDs with namespace and metadata.
- `SearchConfig`: Retrieval configuration (encoder name, `top_k`, `rerank_k`, optional rerank model, metadata filters,
  hybrid weights).

## Client (`meshmind/client.py`)
- `MeshMind` bootstraps:
  - Default OpenAI client (Responses API) when the SDK is installed; custom clients can be injected for testing. A provider-agnostic
    wrapper is planned so future sessions can swap endpoints/models without touching call sites (see `TODO.md`).
  - Embedding model from configuration with encoder bootstrap that registers available adapters.
  - Graph driver factory that creates the configured backend (memory, SQLite, Memgraph, Neo4j) lazily when persistence is required.
- Provides convenience helpers:
  - Pipelines: `extract_memories`, `deduplicate`, `score_importance`, `compress`, `store_memories`, `store_triplets`.
  - CRUD: `create_memory`, `update_memory`, `delete_memory`, `get_memory`,
    `list_memories(namespace=None, entity_labels=None, offset=0, limit=None, query=None, use_search=None)`,
    `memory_counts`, `list_triplets`.
  - Retrieval: `search` (hybrid + optional LLM rerank), `search_vector`, `search_regex`, `search_exact` with automatic graph-backed loading when `memories` is omitted.
- Exposes `graph_driver`/`driver` properties that surface the active graph driver instance on demand.

## Embeddings & Utilities (`meshmind/core/embeddings.py`, `meshmind/core/utils.py`)
- `EncoderRegistry` manages encoder instances (OpenAI embeddings, sentence-transformers, custom fixtures).
- OpenAI and SentenceTransformer adapters provide encoding with retry logic and optional fallbacks.
- Utility functions provide UUIDs, timestamps, hashing, and token counting guarded behind optional `tiktoken` imports.

## Database Layer (`meshmind/db`)
- `GraphDriver` defines the persistence contract (entity/relationship upserts, querying, deletions, triplet listing) and now standardises pagination (`offset`, `limit`), server-side search (`search_entities`), and aggregated counts (`count_entities`).
- `InMemoryGraphDriver` and `SQLiteGraphDriver` power local development/testing without external services while supporting the extended contract.
- `MemgraphDriver` wraps the `mgclient` module shipped with the `pymgclient` package, handles URI parsing, executes Cypher statements, and exposes Cypher-based filtering,
  pagination, and aggregation helpers alongside the Python-side vector search fallback when database-native similarity is
  unavailable.
- `Neo4jGraphDriver` mirrors the Memgraph contract using the official driver (optional dependency) and now exposes server-side search and counts.
- `factory.py` exposes helpers (`create_graph_driver`, `graph_driver_factory`) to instantiate backends based on configuration.

## Pipeline Modules (`meshmind/pipeline`)
1. **Extraction (`extract.py`)** – Orchestrates OpenAI function calling against the `Memory` schema, enforces entity label filters,
   and populates embeddings via registered encoders.
2. **Preprocess (`preprocess.py`)** – Deduplicates by name/embedding similarity, ensures memories have importance scores while
   recording telemetry statistics, and delegates to compression when available.
3. **Compress (`compress.py`)** – Truncates metadata payloads to configurable token budgets when `tiktoken` is installed and records telemetry counters/durations.
4. **Store (`store.py`)** – Persists memories and triplets using the configured `GraphDriver`, registering predicates as needed and emitting observability events.
5. **Consolidate & Expire (`consolidate.py`, `expire.py`)** – Maintenance utilities triggered by Celery tasks to group memories,
   apply batch/backoff settings, surface skipped groups, and remove stale entries.

## Service Layers (`meshmind/api`)
- `memory_manager.py`: CRUD façade over the active graph driver that forwards namespace/entity-label filters, pagination hints, search strings, and exposes aggregate counts alongside triplet listings.
- `service.py`: Pydantic payloads and orchestration helpers shared by REST/gRPC surfaces. `MemoryService.search` leans on driver-side filtering before ranking and exposes `memory_counts` for CLI/HTTP usage.
- `rest.py`: `create_app` returns a FastAPI application when available or a `RestAPIStub` for tests. Routes support pagination parameters and include `/memories/counts` for namespace/label summaries.
- `grpc.py`: `GrpcServiceStub` plus simple request/response dataclasses mirroring planned RPCs.

## Retrieval (`meshmind/retrieval`)
- `filters.py`: Namespace, entity label, and metadata filtering helpers.
- `bm25.py`, `fuzzy.py`: Lexical and fuzzy scorers using scikit-learn TF-IDF + cosine and RapidFuzz WRatio, with pure-Python fallbacks when optional dependencies are unavailable.
- `vector.py`: Vector-only search utilities with cosine similarity and optional precomputed query embeddings.
- `hybrid.py`: Combines vector and BM25 scores with configurable weights defined in `SearchConfig`.
- `search.py`: Dispatchers for hybrid, BM25, fuzzy, vector, regex, and exact-match search modes plus metadata filters.
- `rerank.py`: Generic reranker interface and LLM-based rerank helper compatible with the OpenAI Responses API.
- `graph.py`: Wrappers that pull candidates from the active graph driver before delegating to the existing search strategies.

## CLI (`meshmind/cli`)
- `meshmind.cli.__main__`: Entry point exposing `ingest` and `admin` subcommands for local pipelines and maintenance tooling.
- CLI bootstraps encoder and entity registries, validates configuration early, surfaces actionable errors when optional
  dependencies are missing, and routes predicate maintenance, telemetry inspection, and graph connectivity checks through
  `meshmind.cli.admin`.

## Tasks (`meshmind/tasks`)
- `celery_app.py`: Creates the Celery application lazily, returning a shim when Celery is not installed.
- `scheduled.py`: Defines periodic consolidation, compression, and expiry jobs that initialize drivers and managers lazily,
  emit observability events, persist updated memories, surface skipped consolidation groups, and tolerate missing dependencies
  during import.

## API Adapter (`meshmind/api/memory_manager.py`)
- Manages CRUD operations against the graph driver, including triplet persistence and deletion helpers.
- Returns Pydantic models for list/get operations and gracefully handles missing records.

## Models (`meshmind/models/registry.py`)
- `EntityRegistry` and `PredicateRegistry` store class metadata and permitted predicates.
- Registries are populated during bootstrap and extended as new entity/predicate types are defined.

## Examples & Tests
- `examples/extract_preprocess_store_example.py`: Demonstrates extraction, preprocessing, triplet creation, and multiple
  retrieval strategies.
- `meshmind/tests`: Pytest suites rely on fixtures (`memory_factory`, `dummy_encoder`, in-memory drivers, service stubs) and
  pure-Python doubles (compatibility BaseModel, fake Memgraph/Redis/embedding drivers), allowing the suite to run without Memgraph, OpenAI, or Redis dependencies.

- Required: `openai`, `pydantic`, `pydantic-settings`, `python-dotenv`. Install `pymgclient` (for the runtime `mgclient` module) when using Memgraph and install the `neo4j`
  driver when targeting Neo4j. Pure-Python fallbacks exist for Pydantic, numpy, scikit-learn, and rapidfuzz but production deployments
  should install the real packages.
- Optional but supported: `tiktoken`, `sentence-transformers`, `celery[redis]`, `fastapi`, `uvicorn[standard]`, `redis`, `httpx`,
  `pytest-cov`.
- Development tooling introduced in the Makefile/CI expects `ruff`, `pyright`, `typeguard`, `toml-sort`, `yamllint`, `mkdocs`, and
  `mkdocs-material` (now bundled in the extras).

## Operational Notes
- Graph persistence requires a configured backend: in-memory/SQLite need no services; Memgraph requires a running instance
  reachable via `settings.MEMGRAPH_URI` and the `mgclient` module provided by `pymgclient`; Neo4j requires the official driver and credentials. Use `meshmind admin graph --backend <name>` to sanity check connectivity or run the compose stacks.
- Encoder registration occurs during bootstrap; ensure at least one embedding encoder is available before extraction/search.
- LLM reranking uses the OpenAI Responses API. Provide `OPENAI_API_KEY` and confirm the selected `SearchConfig.rerank_model` is
  deployed to your account.
- Local development commands rely on external tooling (ruff, pyright, typeguard, toml-sort, yamllint); install them via the
  Makefile or the CI workflow instructions in `README.md`.
- Docker Compose can be used to run Memgraph/Neo4j/Redis locally; ensure container tooling is available or provision services
  manually.
