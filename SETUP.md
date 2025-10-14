# Setup Guide

This guide walks through preparing a MeshMind development machine, provisioning the
external graph/cache services, and validating that the environment is ready for local
execution and automated testing.

## 1. Prerequisites

- **Operating system**: Linux or macOS with Docker Engine ≥ 24 and Docker Compose v2.
- **Python**: CPython 3.11.x (the project currently supports 3.11 and 3.12).
- **System packages** (only required if you intend to install optional graph drivers):
  - Build tooling: `build-essential`, `cmake`, `git`.
  - Crypto/Kerberos headers: `libssl-dev`, `libkrb5-dev` (for `mgclient`).
  - Optional: `libopenblas-dev` for faster `numpy`/`scikit-learn` builds on Debian/Ubuntu.
- **Automation scripts**: `run/install_setup.sh` bootstraps a fresh environment; `run/maintenance_setup.sh` refreshes a cached
  workspace. Both require sudo/root access and outbound internet connectivity.

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
   uv pip install --system -e .[dev,docs,testing]  # omit --system when inside an active virtualenv
   ```

   The editable install pulls in the optional dependencies used by the REST service
   (`fastapi`, `uvicorn`), the graph drivers (`neo4j`, `mgclient`, `redis`), LLM tooling
   (`openai`, `tiktoken`, `sentence-transformers`), and developer utilities (ruff,
   pyright, typeguard, docs tooling, pytest plugins).

3. Copy the sample environment file and adjust values as needed:

   ```bash
   cp .env.example .env
   ```

## 3. Provision external services

The repository ships with a root `docker-compose.yml` that starts Redis, Memgraph, and
Neo4j with sane defaults. Run the stack in the background:

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
| `full-stack.yml` | Spins up all services plus an optional Celery worker. |

Example (Memgraph only):

```bash
docker compose -f meshmind/tests/docker/memgraph.yml up -d
```

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
| `OPENAI_API_KEY` | Key for OpenAI embedding endpoints. | _none_ |
| `SENTENCE_TRANSFORMERS_MODEL` | HuggingFace model ID used for local embeddings. | `all-MiniLM-L6-v2` |
| `DEFAULT_ENCODER` | Preferred encoder alias (`openai` or `sentence-transformers`). | `sentence-transformers` |

Optional variables for experimentation:

- `SQLITE_PATH` – override the path for the SQLite prototype driver.
- `GRAPH_BACKEND` – choose between `memory`, `sqlite`, `memgraph`, and `neo4j`.
- `CELERY_BROKER_URL` – override the broker used by Celery (defaults to `REDIS_URL`).

## 5. Smoke tests

After installing dependencies and starting the services:

```bash
make test
meshmind admin graph --backend memgraph
meshmind admin graph --backend neo4j
meshmind admin counts --backend sqlite
```

You should see passing pytest output and successful graph connectivity checks. Refer to
`docs/troubleshooting.md` if any of the services fail health checks.
