# Tasks for Human Project Manager

- Keep the Python package layer aligned with the project extras during base image
  refreshes. The `run/install_setup.sh` and `run/maintenance_setup.sh` scripts now
  install the full optional stack (neo4j driver, `pymgclient`, Redis, Celery extras,
  FastAPI/Uvicorn, LLM tooling, and developer linters/testers). Ensure cached
  environments either run the maintenance script or bake these dependencies into the
  image so cold starts do not regress coverage.
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
- Supply datasets/fixtures (future request) representing large knowledge graphs to
  stress-test consolidation heuristics and pagination under load.
- Maintain outbound package download access to PyPI and vendor repositories; this
  session confirmed package installation works when the network is open, and future
  sessions need the same capability to refresh locks or install new optional
  integrations.
- Enable Docker or container runtime access (future request) so the provided
  `docker-compose.yml` files can run inside this environment; alternatively, provision
  remote services accessible to CI.
- Document credential management procedures and rotation cadence so secrets stay current.
- Keep gRPC tooling (`grpcio`, `grpcio-tools`, protobuf compiler) available in cached environments; the proto definitions now back the production stubs and need to be regenerated whenever the schema evolves.
