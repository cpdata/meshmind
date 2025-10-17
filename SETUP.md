# Setup Guide

This guide walks through preparing a MeshMind development machine, provisioning the
external graph/cache services, and validating that the environment is ready for local
execution and automated testing.

## 1. Prerequisites

- **Operating system**: Linux or macOS with Docker Engine ≥ 24 and Docker Compose v2.
- **Python**: CPython 3.11.x (the project currently supports 3.11 and 3.12).
- **System packages** (only required if you intend to install optional graph drivers):
  - Build tooling: `build-essential`, `cmake`, `git`.
- Crypto/Kerberos headers: `libssl-dev`, `libkrb5-dev` (needed to compile `pymgclient`, which provides the `mgclient` module).
  - Optional: `libopenblas-dev` for faster `numpy`/`scikit-learn` builds on Debian/Ubuntu.
- **Automation scripts**: `run/install_setup.sh` bootstraps a fresh environment; `run/maintenance_setup.sh` refreshes a cached
  workspace. Each script checks that the optional extras (`fastapi`, `neo4j`, `pymgclient`, `uvicorn`) are declared in
  `pyproject.toml`, installs `uv` if necessary, and either synchronizes from `uv.lock` or performs a validation-only dry run
  when `MESH_SKIP_SYSTEM_PACKAGES=1` and/or `MESH_SKIP_PYTHON_SYNC=1` are set. The pytest suite exercises this behaviour in
  `meshmind/tests/test_setup_scripts.py`.

## 2. Bootstrap the Python environment

1. Create and activate a virtual environment:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. Install MeshMind and all optional extras required for full local coverage:

   ```bash
   python -m pip install --upgrade pip
   pip install uv
   uv python pin 3.12      # keeps `.python-version` aligned with the supported range
   uv sync --all-extras    # installs the project plus dev/docs/testing extras into .venv
   ```

   The sync command honours `uv.lock` and pulls in the optional dependencies used by
   the REST service (`fastapi`, `uvicorn`), the graph drivers (`neo4j`, `pymgclient`,
   `redis`), LLM tooling (`openai`, `tiktoken`, `sentence-transformers`), and developer
   utilities (ruff, pyright, typeguard, docs tooling, pytest plugins).

3. Copy the sample environment file and adjust values as needed:

   ```bash
   cp .env.example .env
   ```

## 3. Provision external services

The repository ships with a root `docker-compose.yml` that starts Redis, Memgraph,
Neo4j, the gRPC API server, and the Celery worker with sane defaults. Run the stack in
the background:

```bash
docker compose up -d
```

> The default Neo4j credentials are `neo4j` / `meshminD123`. Memgraph exposes Bolt on
> `bolt://localhost:7687`, the Memgraph Lab UI on `http://localhost:3000`, and an
> additional monitoring endpoint on `http://localhost:7444`.

### 3.1 Alternate topologies for tests

For integration scenarios or CI jobs, use the compose files in
`meshmind/tests/docker/`:

| File | Purpose |
| --- | --- |
| `memgraph.yml` | Runs only Memgraph with local port mapping. |
| `neo4j.yml` | Runs only Neo4j with APOC enabled. |
| `redis.yml` | Runs only Redis with persistence. |
| `full-stack.yml` | Spins up all services, the Celery worker, and the gRPC server. |

Example (Memgraph only):

```bash
docker compose -f meshmind/tests/docker/memgraph.yml up -d
```

> Need synthetic load? Run `python scripts/generate_synthetic_dataset.py build/datasets/benchmark`
> to seed JSONL/CSV fixtures before loading them into Memgraph/Neo4j for stress tests. Triplet rows
> now include `entity_label`, so the ingestion workflow in `docs/retrieval.md` can materialize
> `Triplet` models without mutating CSV fields. Follow the ingestion steps when copying fixtures so
> benchmarks reuse the same namespace/layout.

### 3.2 Cleaning up

```bash
docker compose down -v
```

## 4. Configure environment variables

Update `.env` (or export variables in your shell) with the credentials for each
service:

| Variable | Description | Default |
| --- | --- | --- |
| `MEMGRAPH_URI` | Bolt URI for Memgraph. | `bolt://localhost:7687` |
| `NEO4J_URI` | Bolt URI for Neo4j. | `bolt://localhost:7688` |
| `NEO4J_USERNAME` / `NEO4J_PASSWORD` | Neo4j auth values. | `neo4j` / `meshminD123` |
| `REDIS_URL` | Redis connection string. | `redis://localhost:6379/0` |
| `LLM_API_KEY` / `OPENAI_API_KEY` | API key for OpenAI-compatible providers (OpenAI, OpenRouter, Azure, Google). | _none_ |
| `LLM_DEFAULT_MODEL` | Default Responses model for extraction/rerank. | `gpt-5-nano` |
| `LLM_DEFAULT_BASE_URL` | Default base URL for OpenAI-compatible SDKs. | `https://api.openai.com/v1` |
| `LLM_EXTRACTION_MODEL` / `LLM_EXTRACTION_BASE_URL` | Overrides for extraction requests. | inherit defaults |
| `LLM_EMBEDDING_MODEL` / `LLM_EMBEDDING_BASE_URL` | Overrides for embedding requests. | `text-embedding-3-small` / empty |
| `LLM_RERANK_MODEL` / `LLM_RERANK_BASE_URL` | Overrides for reranking requests. | inherit defaults |
| `MAINTENANCE_MAX_ATTEMPTS` | Retry attempts for maintenance writes. | `3` |
| `MAINTENANCE_BASE_DELAY_SECONDS` | Base delay (seconds) for exponential maintenance backoff. | `1.0` |
| `SENTENCE_TRANSFORMERS_MODEL` | HuggingFace model ID used for local embeddings. | `all-MiniLM-L6-v2` |
| `DEFAULT_ENCODER` | Preferred encoder alias (`openai` or `sentence-transformers`). | `sentence-transformers` |

Optional variables for experimentation:

- `SQLITE_PATH` – override the path for the SQLite prototype driver.
- `GRAPH_BACKEND` – choose between `memory`, `sqlite`, `memgraph`, and `neo4j`.
- `CELERY_BROKER_URL` – override the broker used by Celery (defaults to `REDIS_URL`).
- `LLM_*` variables – adjust endpoint/model overrides per operation when targeting non-default LLM providers.
- `MAINTENANCE_MAX_ATTEMPTS` / `MAINTENANCE_BASE_DELAY_SECONDS` – tune consolidation/compression retries for your deployment.

## 5. Smoke tests

After installing dependencies and starting the services:

```bash
make test
pytest -m integration                # requires docker compose up -d
meshmind admin graph --backend memgraph
meshmind admin graph --backend neo4j
meshmind admin counts --backend sqlite
```

You should see passing unit tests, integration output, and successful graph
connectivity checks. Refer to `docs/troubleshooting.md` if any of the services
fail health checks.

To validate the gRPC surface locally:

```bash
meshmind serve-grpc --host 0.0.0.0 --port 50051 --backend memgraph
grpcurl -plaintext -d '{"namespace":"demo"}' localhost:50051 meshmind.api.MemoryService/MemoryCounts
```

Stop the server with `Ctrl+C` when finished (the CLI handles graceful shutdown).
