# Troubleshooting

## Optional Tooling Installation Failures

- **Ruff, Pyright, Typeguard**
  - Install via `uv pip install ruff pyright typeguard` to match CI tooling.
  - If Pyright is unavailable, run `make lint` to exercise Ruff only and document the gap in `ENVIRONMENT_NEEDS.md`.
- **toml-sort / yamllint**
  - Provided through `uv pip install toml-sort yamllint`.
  - When installing globally, ensure the binaries are on the `PATH` or invoke via `python -m toml_sort` and `python -m yamllint`.

## Graph Backends

- **Memgraph / Neo4j connectivity**
  - Verify credentials are exported (`MEMGRAPH_URI`, `NEO4J_URI`, etc.) before running `mesh admin graph --backend neo4j`.
  - When the native drivers are unavailable, fall back to the in-memory or SQLite backends and note the blocker in `ENVIRONMENT_NEEDS.md`.

## External Services

- **Redis**
  - Use `docker-compose up redis` to start the local stack, or swap in the `FakeRedisBroker` for unit tests.
- **Embedding providers**
  - When `LLM_API_KEY`/`OPENAI_API_KEY` are missing, configure `FAKE_EMBEDDINGS=1` to rely on the deterministic fake encoder
    or point `LLM_EMBEDDING_MODEL`/`LLM_EMBEDDING_BASE_URL` at a provider accessible in your environment.

## Common Runtime Symptoms

- **Search returns empty results**
  - Confirm that the namespace and `entity_labels` filters align with persisted memories.
  - For graph-backed searches, run `mesh admin counts` to validate stored entity counts.
- **Pagination behaves unexpectedly**
  - Inspect driver-specific logs (enable via `MESH_LOG_LEVEL=DEBUG`) to confirm the offset and limit values passed downstream.
