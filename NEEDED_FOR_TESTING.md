# Needed for Testing MeshMind

> **Note:** `ENVIRONMENT_NEEDS.md` lists infrastructure and package requests for the human project manager. Use this document for developer-side setup details.

## Python Runtime
- Python 3.11 or 3.12 is recommended; project metadata now pins `>=3.11,<3.13` because several dependencies (`pymgclient` (exposes the `mgclient` module),
  `sentence-transformers`) do not yet publish wheels for 3.13.
- Use a virtual environment (`uv`, `venv`, or `conda`) to isolate dependencies.

## Python Dependencies
- Install the project editable (with extras) using `uv sync --all-extras` (preferred; honours `uv.lock` and the repository's
  `.python-version`) or `pip install -e .[dev,docs,testing]` if `uv` is unavailable.
- Core functionality relies on the OpenAI SDK (or compatible fork), `pydantic`, and `pydantic-settings`; the project now
  requires Pydantic 2.x directly (the legacy shim has been removed).
- Optional packages improve specific workflows (now bundled in the editable install extras so they install automatically when
  running the provisioning scripts):
  - `numpy`, `scikit-learn`, and `rapidfuzz` accelerate similarity and lexical search (pure-Python fallbacks are bundled).
  - `sentence-transformers`, `tiktoken`, and `pymgclient` enable local embeddings, compression, and Memgraph connectivity.
  - `celery[redis]` activates scheduled maintenance with a Redis broker.
  - `fastapi` + `uvicorn[standard]` power the REST adapter when exercising HTTP APIs.
  - `grpcio` + `grpcio-tools` + `protobuf` enable the generated gRPC clients/servers that replace the former dataclass shim.
- Optional drivers: install `neo4j` if exercising the Neo4j backend; SQLite support ships with the standard library. The
  provisioning scripts validate that the extras expose `neo4j`, `pymgclient`, `fastapi`, and `uvicorn`.
- Development tooling referenced by the Makefile and CI (installed via `.[dev,docs,testing]`):
  - `ruff` for linting and formatting.
  - `pyright` for static type checks.
  - `typeguard` for runtime type enforcement (`python -m typeguard --check meshmind`).
  - `toml-sort` and `yamllint` for configuration validation.
  - `mkdocs`/`mkdocs-material` for future documentation publishing.
- Optional helpers for local workflows: `pytest-cov`, `pre-commit`, `httpx`/`grpcio-tools` (for service interface experimentation).

## External Services and Infrastructure
- **Graph backend** options:
  - In-memory / SQLite require no external services (set `GRAPH_BACKEND=memory` or `sqlite`).
  - **Memgraph** reachable via `MEMGRAPH_URI` with credentials exported in `MEMGRAPH_USERNAME`/`MEMGRAPH_PASSWORD`.
  - **Neo4j** reachable via `NEO4J_URI` with credentials `NEO4J_USERNAME`/`NEO4J_PASSWORD` when the optional driver is installed
    (defaults supplied in `docker-compose.yml`). Use `meshmind admin graph --backend neo4j` to verify connectivity once
    credentials are configured.
- **Redis** for Celery task queues, referenced through `REDIS_URL`.
- **LLM provider access** for extraction, embeddings, and reranking (`LLM_API_KEY` or fallback `OPENAI_API_KEY`, plus optional
  `LLM_*_BASE_URL` overrides for alternative providers).
- Recommended: Docker Compose (shipped in repo) to run Memgraph, Neo4j, and Redis together when developing locally. Start the
  root stack with `docker compose up -d` before executing `pytest -m integration`; targeted stacks live under
  `meshmind/tests/docker/` for focused scenarios.

## Environment Variables
- `GRAPH_BACKEND` — `memory`, `sqlite`, `memgraph`, or `neo4j` (defaults to `memory`).
- `LLM_API_KEY` / `OPENAI_API_KEY` — required for extraction, embeddings, and reranking (OpenAI-compatible providers).
- `LLM_DEFAULT_MODEL` / `LLM_DEFAULT_BASE_URL` — default Responses model/base URL applied when overrides are absent.
- `LLM_EXTRACTION_MODEL` / `LLM_EXTRACTION_BASE_URL` — optional overrides for extraction calls.
- `LLM_EMBEDDING_MODEL` / `LLM_EMBEDDING_BASE_URL` — optional overrides for embedding requests.
- `LLM_RERANK_MODEL` / `LLM_RERANK_BASE_URL` — optional overrides for reranking requests.
- `MEMGRAPH_URI` — e.g., `bolt://localhost:7687` (when using Memgraph).
- `MEMGRAPH_USERNAME` and `MEMGRAPH_PASSWORD` — credentials for the Memgraph database.
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — optional Neo4j connectivity details.
- `SQLITE_PATH` — filesystem path for the SQLite graph backend (defaults to in-memory).
- `REDIS_URL` — optional Redis connection URI (defaults to `redis://localhost:6379/0`).
- `EMBEDDING_MODEL` — legacy alias for the embedding encoder key (defaults to `LLM_EMBEDDING_MODEL`).
- `MAINTENANCE_MAX_ATTEMPTS` — retry attempts for consolidation/compression writes (defaults to `3`).
- `MAINTENANCE_BASE_DELAY_SECONDS` — base delay used for exponential backoff (defaults to `1.0`).
- Optional overrides for Celery broker/backend if using hosted services.

## Local Configuration Steps
- Ensure an embedding encoder is registered before extraction or hybrid search. The bootstrap utilities invoked by the CLI and
  `MeshMind` constructor handle this, but custom scripts must call `bootstrap_encoders()`.
- For REST/gRPC testing, instantiate the FastAPI app via `meshmind.api.rest.create_app`
  and exercise it with `fastapi.testclient.TestClient` (requires the `httpx`
  package); pair it with the `GrpcServiceStub` for lightweight gRPC coverage when
  external services are unavailable.
- Use `meshmind/testing` fakes (`FakeMemgraphDriver`, `FakeRedisBroker`, `FakeEmbeddingEncoder`, `FakeLLMClient`) in tests or demos to eliminate external infrastructure requirements. Integration suites marked with `@pytest.mark.integration` exercise live Memgraph/Neo4j/Redis instances and expect the docker stack to be running.
- Invoke `meshmind admin predicates` and `meshmind admin maintenance --max-attempts <n> --base-delay <seconds> --run <task>` during local runs to inspect predicate registries, telemetry, and tune maintenance retries without external services.
- Use the benchmarking utilities in `scripts/` (`evaluate_importance.py`, `consolidation_benchmark.py`, `benchmark_pagination.py`) to validate heuristics and driver performance offline before connecting to live infrastructure. Generate large corpora with `scripts/generate_synthetic_dataset.py` when you need ≥10k memories for stress tests and follow the ingestion workflow in `docs/retrieval.md` to load them into the graph drivers used by your tests.
- Seed demo data as needed using the `examples/extract_preprocess_store_example.py` script after configuring environment
  variables.
- Create a `.env` file storing the environment variables above for consistent local configuration.

## Current Blockers in This Environment
- External network restrictions may limit installation of proprietary packages or access to OpenAI-compatible endpoints.
