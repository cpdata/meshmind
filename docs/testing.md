# Testing & Quality

MeshMind includes an extensive pytest suite that runs without external services by relying on fake drivers and in-memory
backends.

## Test Topology

- `meshmind/tests/test_pipeline_*`: validate extraction, preprocessing, storage, and maintenance flows with dummy
  drivers.
- `meshmind/tests/test_db_*`: ensure graph drivers implement CRUD semantics (with fakes for optional dependencies).
- `meshmind/tests/test_retrieval.py` and `test_graph_retrieval.py`: exercise hybrid, textual, vector, and graph-based
  searches.
- `meshmind/tests/test_service_interfaces.py`: cover REST and gRPC stubs, including entity-label filtering, pagination hints, and memory count routes with LLM override payloads.
- `meshmind/tests/test_setup_scripts.py`: run the provisioning scripts in validation mode to ensure optional dependencies are declared in `pyproject.toml`, that `uv` is bootstrapped, and that skip flags behave as expected.
- `meshmind/tests/test_cli_admin.py`: verify administrative CLI commands use the correct driver factory, settings, and counts reporting.
- `meshmind/tests/test_counts_smoke.py`: exercise the REST `/memories/counts` endpoint and `meshmind admin counts` command against the in-memory driver as smoke coverage.
- `meshmind/tests/test_tasks_scheduled.py`: assert maintenance consolidation retries handle transient conflicts via configurable backoff.
- `meshmind/tests/test_docs_guard.py`: ensure the documentation guard script enforces wiki updates when code modules change.
- `meshmind/tests/test_observability.py`: confirm telemetry metrics/counters update during preprocessing steps.
- `meshmind/tests/test_benchmark_scripts.py`: smoke the benchmarking CLI utilities (`scripts/evaluate_importance.py`, `scripts/consolidation_benchmark.py`, `scripts/benchmark_pagination.py`).
- `meshmind/tests/test_api_examples.py`: validate the documented curl/grpcurl payloads against the FastAPI app and gRPC stub.

## Fakes & Fixtures

- `meshmind.testing.fakes`: supplies fake Memgraph/Redis/embedding drivers and a provider-agnostic `FakeLLMClient` that records
  override dictionaries (`llm_models`, `llm_base_urls`, `llm_api_key`) so service tests can assert cascading behaviour without
  real SDK calls.
- `meshmind/tests/conftest.py`: defines reusable fixtures such as `dummy_encoder`, `memory_service`, and telemetry reset
  helpers.
- `DUMMIES.md`: outlines every compatibility shim and stub so test suites can migrate toward real dependencies over time.

## Running Tests

```bash
pip install -e .[dev,docs,testing]
pytest
```

Optional extras:

- `PYTHONPATH=.` ensures imports resolve when running tests manually.
- To test the Neo4j/Memgraph drivers, set `GRAPH_BACKEND` appropriately, point `MEMGRAPH_URI` / `NEO4J_URI` at the Docker
  services, and export credentials as described in `SETUP.md` and `ENVIRONMENT_NEEDS.md`.

## Benchmarking Scripts

MeshMind ships synthetic benchmarks that exercise the importance heuristic, consolidation planner, and graph pagination
behaviour. Run them locally with the provided Make target:

```bash
make benchmarks
```

The command stores JSON summaries under `build/benchmarks/`:

- `importance.json` – descriptive statistics for the heuristic across synthetic memories.
- `consolidation.json` – retry counts, removals, and latency distributions for consolidation batches.
- `pagination.json` – pagination duration and fetch counts for the configured graph backend (defaults to the in-memory driver).

Adjust the script flags (for example `--backend`, `--iterations`, or `--count`) to stress alternative drivers or larger
datasets; see `scripts/*.py` for supported options. Document notable findings in `FINDINGS.md` or `ENVIRONMENT_NEEDS.md`
when tuning defaults for new environments.

## Adding Tests

1. Prefer deterministic unit tests using the in-memory driver or fakes.
2. When touching new modules, add coverage in the closest existing test file or create a dedicated module under
   `meshmind/tests`.
3. Mock optional dependencies (`LLMClient` providers, Redis, Celery) unless integration coverage is explicitly required.
4. Update documentation (`docs/testing.md`, `README.md`) whenever the testing workflow changes.
