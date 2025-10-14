# Needed for Testing MeshMind

## Python Runtime
- Python 3.11 or 3.12 is recommended; project metadata claims 3.13+, but several dependencies (e.g., `pymgclient`, `sentence-transformers`)
  have not been validated there.
- A virtual environment (via `venv`, `uv`, or `conda`) to isolate dependencies.

## Python Dependencies
- Install the project in editable mode: `pip install -e .` from the repository root.
- Ensure optional extras that ship as hard dependencies in `pyproject.toml` are present:
  - `pymgclient` for Memgraph connectivity.
  - `celery[redis]` for scheduled maintenance tasks.
  - `tiktoken`, `sentence-transformers`, `rapidfuzz`, `scikit-learn`, and `numpy` for embedding, retrieval, and compression.
- Additional development tooling that may be required when running the current test suite:
  - `pytest` (already listed but verify it installs successfully under the chosen Python version).
  - `python-dotenv` if you plan to load environment variables from a `.env` file.

## External Services and Infrastructure
- **Memgraph** (preferred) or a Neo4j-compatible Bolt graph database reachable at the URI exported via `MEMGRAPH_URI`.
  - Requires the Bolt port (default `7687`) to be exposed.
  - Ensure user credentials provided in `MEMGRAPH_USERNAME` and `MEMGRAPH_PASSWORD` have write access.
- **Redis** instance when exercising Celery tasks (expiry, consolidation, compression). Set its location via `REDIS_URL`.
- **OpenAI API access** for extraction and embedding encoders used throughout the pipeline.
- Optional but useful: an orchestration layer (Docker Compose or Kubernetes) to manage Memgraph and Redis in tandem if you plan to
  mimic production workflows.

## Environment Variables
- `OPENAI_API_KEY` — required for any extraction or embedding calls via the OpenAI SDK.
- `MEMGRAPH_URI` — Bolt connection string, e.g., `bolt://localhost:7687`.
- `MEMGRAPH_USERNAME` — username for the Memgraph (or Neo4j) instance.
- `MEMGRAPH_PASSWORD` — password for the database user.
- `REDIS_URL` — Redis connection URI (defaults to `redis://localhost:6379/0`).
- `EMBEDDING_MODEL` — key used by `EncoderRegistry` (defaults to `text-embedding-3-small`). Ensure a matching encoder is
  registered at runtime before running ingestion or retrieval steps.

## Local Configuration Steps
- Register an embedding encoder before tests that rely on embeddings:
  ```python
  from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder
  EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder("text-embedding-3-small"))
  ```
- Provide seed data or fixtures for the graph database if end-to-end tests assume pre-existing memories.
- Optionally create a `.env` file mirroring the environment variables above for convenient local setup.

## Current Blockers in This Environment
- Neo4j and Memgraph binaries are not available, and container tooling (Docker, `mgconsole`, `neo4j-admin`) cannot be installed,
  preventing local graph database provisioning inside this workspace.
- Outbound network restrictions may block installation of proprietary dependencies or remote database provisioning without
  pre-baked artifacts.
- Redis is likewise unavailable without Docker or host-level package managers; Celery tasks cannot be validated locally until a
  remote instance is supplied.
