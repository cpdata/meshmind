# Testing & Quality

MeshMind includes an extensive pytest suite that runs without external services by relying on fake drivers and in-memory
backends.

## Test Topology

- `meshmind/tests/test_pipeline_*`: validate extraction, preprocessing, storage, and maintenance flows with dummy
  drivers.
- `meshmind/tests/test_db_*`: ensure graph drivers implement CRUD semantics (with fakes for optional dependencies).
- `meshmind/tests/test_retrieval.py` and `test_graph_retrieval.py`: exercise hybrid, textual, vector, and graph-based
  searches.
- `meshmind/tests/test_service_interfaces.py`: cover REST and gRPC stubs, including entity-label filtering, pagination hints, and memory count routes.
- `meshmind/tests/test_cli_admin.py`: verify administrative CLI commands use the correct driver factory, settings, and counts reporting.
- `meshmind/tests/test_docs_guard.py`: ensure the documentation guard script enforces wiki updates when code modules change.
- `meshmind/tests/test_observability.py`: confirm telemetry metrics/counters update during preprocessing steps.

## Fakes & Fixtures

- `meshmind.testing.fakes`: supplies fake Memgraph/Redis/embedding drivers to avoid optional dependency installs.
- `meshmind/tests/conftest.py`: defines reusable fixtures such as `dummy_encoder`, `memory_service`, and telemetry reset
  helpers.

## Running Tests

```bash
pip install -e .[dev]
pytest
```

Optional extras:

- `PYTHONPATH=.` ensures imports resolve when running tests manually.
- To test the Neo4j/Memgraph drivers, set `GRAPH_BACKEND` appropriately and provide connection URIs (see
  `ENVIRONMENT_NEEDS.md`).

## Adding Tests

1. Prefer deterministic unit tests using the in-memory driver or fakes.
2. When touching new modules, add coverage in the closest existing test file or create a dedicated module under
   `meshmind/tests`.
3. Mock optional dependencies (OpenAI, Redis, Celery) unless integration coverage is explicitly required.
4. Update documentation (`docs/testing.md`, `README.md`) whenever the testing workflow changes.
