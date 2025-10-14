# Needed for Testing MeshMind

> **Note:** `ENVIRONMENT_NEEDS.md` lists infrastructure and package requests for the human project manager. Use this document for developer-side setup details.

## Python Runtime
- Python 3.11 or 3.12 is recommended; project metadata now pins `>=3.11,<3.13` because several dependencies (`pymgclient` (exposes the `mgclient` module),
  `sentence-transformers`) do not yet publish wheels for 3.13.
- Use a virtual environment (`uv`, `venv`, or `conda`) to isolate dependencies.

## Python Dependencies
- Install the project editable (with extras) using `pip install -e .[dev,docs,testing]` or
  `uv pip install --system -e .[dev,docs,testing]` from the repository root.
- Core functionality relies on `openai`, `pydantic`, and `pydantic-settings`, but the repository ships a compatibility shim
  (`meshmind/_compat/pydantic.py`) that unlocks tests when Pydantic is unavailable.
- Optional packages improve specific workflows (most now included via the extras above):
  - `numpy`, `scikit-learn`, and `rapidfuzz` accelerate similarity and lexical search (pure-Python fallbacks are bundled).
  - `sentence-transformers`, `tiktoken`, and `pymgclient` enable local embeddings, compression, and Memgraph connectivity.
  - `celery[redis]` activates scheduled maintenance with a Redis broker.
  - `fastapi` + `uvicorn[standard]` power the REST adapter when exercising HTTP APIs.
- Optional drivers: install `neo4j` if exercising the Neo4j backend; SQLite support ships with the standard library.
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
-  - **Memgraph** reachable via `MEMGRAPH_URI` with credentials exported in `MEMGRAPH_USERNAME`/`MEMGRAPH_PASSWORD`.
-  - **Neo4j** reachable via `NEO4J_URI` with credentials `NEO4J_USERNAME`/`NEO4J_PASSWORD` when the optional driver is installed
     (defaults supplied in `docker-compose.yml`). Use `meshmind admin graph --backend neo4j` to verify connectivity once
     credentials are configured.
- **Redis** for Celery task queues, referenced through `REDIS_URL`.
- **OpenAI API access** for extraction, embeddings, and LLM reranking (`OPENAI_API_KEY`).
- Recommended: Docker Compose (shipped in repo) to run Memgraph, Neo4j, and Redis together when developing locally. Additional
  targeted stacks live under `meshmind/tests/docker/` for integration tests.

## Environment Variables
- `GRAPH_BACKEND` — `memory`, `sqlite`, `memgraph`, or `neo4j` (defaults to `memory`).
- `OPENAI_API_KEY` — required for extraction, embeddings, and reranking.
- `MEMGRAPH_URI` — e.g., `bolt://localhost:7687` (when using Memgraph).
- `MEMGRAPH_USERNAME` and `MEMGRAPH_PASSWORD` — credentials for the Memgraph database.
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — optional Neo4j connectivity details.
- `SQLITE_PATH` — filesystem path for the SQLite graph backend (defaults to in-memory).
- `REDIS_URL` — optional Redis connection URI (defaults to `redis://localhost:6379/0`).
- `EMBEDDING_MODEL` — encoder key registered with `EncoderRegistry` (defaults to `text-embedding-3-small`).
- Optional overrides for Celery broker/backend if using hosted services.

## Local Configuration Steps
- Ensure an embedding encoder is registered before extraction or hybrid search. The bootstrap utilities invoked by the CLI and
  `MeshMind` constructor handle this, but custom scripts must call `bootstrap_encoders()`.
- For REST/gRPC testing, instantiate the `RestAPIStub`/`GrpcServiceStub` with the in-memory driver to avoid external services.
- Use `meshmind/testing` fakes (`FakeMemgraphDriver`, `FakeRedisBroker`, `FakeEmbeddingEncoder`) in tests or demos to eliminate external infrastructure requirements.
- Invoke `meshmind admin predicates` and `meshmind admin maintenance` during local runs to inspect predicate registries and telemetry without external services.
- Seed demo data as needed using the `examples/extract_preprocess_store_example.py` script after configuring environment
  variables.
- Create a `.env` file storing the environment variables above for consistent local configuration.

## Current Blockers in This Environment
- Neo4j/Memgraph binaries and Docker are unavailable in this workspace, preventing local graph provisioning; use the in-memory or SQLite drivers instead.
- Redis cannot be installed without container or host-level access; Celery tasks remain untestable locally until a remote
  instance is provisioned (the fake broker satisfies unit tests but not end-to-end runs).
- External network restrictions may limit installation of proprietary packages or access to OpenAI endpoints.
