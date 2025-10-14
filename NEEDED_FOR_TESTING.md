# Needed for Testing MeshMind

## Python Runtime
- Python 3.11 or 3.12 is recommended; project metadata currently states 3.13+, but several dependencies (`pymgclient`,
  `sentence-transformers`) do not yet publish wheels for 3.13.
- Use a virtual environment (`uv`, `venv`, or `conda`) to isolate dependencies.

## Python Dependencies
- Install the project editable: `pip install -e .` from the repository root.
- Required packages declared in `pyproject.toml` include `openai`, `pydantic`, `pydantic-settings`, `numpy`, `scikit-learn`,
  `rapidfuzz`, `python-dotenv`, `celery[redis]`, `sentence-transformers`, `tiktoken`, and `pymgclient`.
- Development tooling referenced by the Makefile and CI:
  - `ruff` for linting and formatting.
  - `pyright` for static type checks.
  - `typeguard` for runtime type enforcement (`python -m typeguard --check meshmind`).
  - `toml-sort` and `yamllint` for configuration validation.
- Optional helpers for local workflows: `pytest-cov`, `pre-commit`, `httpx` (for future service interfaces).

## External Services and Infrastructure
- **Memgraph** (or compatible Bolt graph database) reachable via `MEMGRAPH_URI` with credentials exported in
  `MEMGRAPH_USERNAME`/`MEMGRAPH_PASSWORD`.
- **Redis** for Celery task queues, referenced through `REDIS_URL`.
- **OpenAI API access** for extraction, embeddings, and LLM reranking (`OPENAI_API_KEY`).
- Recommended: Docker Compose or equivalent orchestration to run Memgraph and Redis together when developing locally.

## Environment Variables
- `OPENAI_API_KEY` — required for extraction, embeddings, and reranking.
- `MEMGRAPH_URI` — e.g., `bolt://localhost:7687`.
- `MEMGRAPH_USERNAME` and `MEMGRAPH_PASSWORD` — credentials for the graph database.
- `REDIS_URL` — optional Redis connection URI (defaults to `redis://localhost:6379/0`).
- `EMBEDDING_MODEL` — encoder key registered with `EncoderRegistry` (defaults to `text-embedding-3-small`).
- Optional overrides for Celery broker/backend if using hosted services.

## Local Configuration Steps
- Ensure an embedding encoder is registered before extraction or hybrid search. The bootstrap utilities invoked by the CLI and
  `MeshMind` constructor handle this, but custom scripts must call `bootstrap_encoders()`.
- Seed demo data as needed using the `examples/extract_preprocess_store_example.py` script after configuring environment
  variables.
- Create a `.env` file storing the environment variables above for consistent local configuration.

## Current Blockers in This Environment
- Neo4j/Memgraph binaries and Docker are unavailable in this workspace, preventing local graph provisioning.
- Redis cannot be installed without container or host-level access; Celery tasks remain untestable locally until a remote
  instance is provisioned.
- External network restrictions may limit installation of proprietary packages or access to OpenAI endpoints.
