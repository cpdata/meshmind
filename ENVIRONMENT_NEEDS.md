# Tasks for Human Project Manager

- Install Python packages required for full optional coverage across CI images and the
  shared development environment:
  - `neo4j` (official Bolt driver).
  - `mgclient` (Memgraph driver).
  - `redis` / `redis-py` for caching tasks.
  - `celery[redis]` for scheduled/async maintenance workers.
  - `fastapi` and `uvicorn[standard]` to exercise the REST API.
  - `tiktoken`, `sentence-transformers`, and `openai` for embedding/compression workflows.
  - `uv` CLI for reproducible dependency management (used in CI).
  - Developer tooling referenced by automation: `ruff`, `pyright`, `typeguard`,
    `toml-sort`, `yamllint`, `pytest-cov`, `httpx`, `mkdocs`, `mkdocs-material`.
- Provide system-level build dependencies for the graph drivers (e.g., `build-essential`,
  `cmake`, `libssl-dev`, `libkrb5-dev`) so `mgclient` installs cleanly.
- Provision external services and credentials (compose files now exist under the project
  root and `meshmind/tests/docker/`):
  - Neo4j instance reachable from the execution environment with `NEO4J_URI`,
    `NEO4J_USERNAME`, `NEO4J_PASSWORD` (defaults to `neo4j` / `meshminD123`).
  - Memgraph instance with `MEMGRAPH_URI`, `MEMGRAPH_USERNAME`, `MEMGRAPH_PASSWORD`
    (anonymous access acceptable locally).
  - Redis instance with `REDIS_URL`.
  - OpenAI API key (`OPENAI_API_KEY`) and, optionally, Azure OpenAI equivalents (future
    integration testing).
- Supply datasets/fixtures (future request) representing large knowledge graphs to
  stress-test consolidation heuristics and pagination under load.
- Allow outbound package downloads to PyPI (current proxy returns HTTP 403, blocking `uv`/dependency lock generation).
- Enable Docker or container runtime access (future request) so the provided
  `docker-compose.yml` files can run inside this environment; alternatively, provision
  remote services accessible to CI.
- Document credential management procedures and rotation cadence so secrets stay current.
