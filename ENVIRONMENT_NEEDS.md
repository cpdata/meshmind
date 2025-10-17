# Tasks for Human Project Manager

- Keep the Python package layer aligned with the project extras during base image
  refreshes. `uv.lock` now targets Python 3.11–3.12 with a default pin of 3.12, and
  the `run/install_setup.sh` / `run/maintenance_setup.sh` scripts call
  `uv sync --all-extras` to install the full stack (neo4j driver, `pymgclient`,
  Redis, Celery extras, FastAPI/Uvicorn, LLM tooling, developer linters/testers).
  Ensure cached environments either run the maintenance script or bake these
  dependencies into the image so cold starts do not regress coverage.
- Provide system-level build dependencies for the graph drivers (e.g., `build-essential`,
  `cmake`, `libssl-dev`, `libkrb5-dev`) so `pymgclient` (and its `mgclient` module) install cleanly.
- Provision external services and credentials (compose files now exist under the project
  root and `meshmind/tests/docker/`):
  - Neo4j instance reachable from the execution environment with `NEO4J_URI`,
    `NEO4J_USERNAME`, `NEO4J_PASSWORD` (defaults to `neo4j` / `meshminD123`).
  - Memgraph instance with `MEMGRAPH_URI`, `MEMGRAPH_USERNAME`, `MEMGRAPH_PASSWORD`
    (anonymous access acceptable locally).
  - Redis instance with `REDIS_URL`.
  - LLM provider API key (`LLM_API_KEY` or fallback `OPENAI_API_KEY`) plus any
    alternative base URLs/models required for OpenRouter, Azure, or Google-hosted
    endpoints so the new `llm_client` overrides can be exercised end-to-end.
  - Default maintenance retry configuration (`MAINTENANCE_MAX_ATTEMPTS`, `MAINTENANCE_BASE_DELAY_SECONDS`) tuned for the deployed graph backend; surface recommended values once integration tests run against live clusters. *(Future refinement request once infra is available.)*
- Supply datasets/fixtures representing large knowledge graphs to stress-test
  consolidation heuristics and pagination under load. The new
  `scripts/generate_synthetic_dataset.py` utility produces JSONL/CSV corpora
  (defaults: 10k memories, 20k triplets, 384-dim embeddings) that can be copied to
  shared storage for on-demand benchmarking. Pair the shared datasets with the
  ingestion workflow documented in `docs/retrieval.md` so operators can seed
  environments quickly without recomputing embeddings.
- Maintain outbound package download access to PyPI and vendor repositories; this
  session confirmed package installation works when the network is open, and future
  sessions need the same capability to refresh locks or install new optional
  integrations.
- Ensure Docker or container runtime access remains available so the root
  `docker-compose.yml` (and targeted stacks under `meshmind/tests/docker/`) can run
  from CI and developer machines. Integration tests now expect these services to be
  reachable via `docker compose up -d` before executing `pytest -m integration`.
- Document credential management procedures and rotation cadence so secrets stay current.
- Keep gRPC tooling (`grpcio`, `grpcio-tools`, protobuf compiler) available in cached environments; the proto definitions now
  back the production stubs and runtime server (`meshmind.api.grpc_server`). `scripts/generate_protos.py` regenerates bindings
  and `scripts/check_protos.py` enforces drift in CI, so ensure the toolchain runs successfully during maintenance scripts.
