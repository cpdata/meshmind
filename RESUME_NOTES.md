# Resume Notes

## Current Context

- Branch: `work` (rebased from `integration`; PR target remains `integration`).
- Optional dependencies ship with the `.[dev,docs,testing]` extras; `uv sync --all-extras` (now pinned to Python 3.12 via `.python-version`) installs FastAPI/Uvicorn, Celery/Redis, Neo4j/Memgraph drivers, LLM tooling, and developer linters. The provisioning scripts in `run/` validate these extras before syncing `uv.lock`.
- Docker orchestration (root `docker-compose.yml` and `meshmind/tests/docker/*.yml`) provisions Memgraph, Neo4j, Redis, the Celery worker, and a gRPC server container; `pytest -m integration` exercises these services once the stack is running.
- Docker orchestration (root `docker-compose.yml` and `meshmind/tests/docker/*.yml`) now provisions Memgraph, Neo4j, Redis, the Celery worker, and a gRPC server container driven by the new CLI command.
- The documentation guard enforces updates whenever code within mapped directories changes; planning artifacts (`PLAN.md`, `PROJECT.md`, `SOT.md`, `ROADMAP.md`, `PLANNING_THOUGHTS.md`, `research/`) remain synchronized per agent instructions.

## Latest Changes

- Added live integration coverage (`meshmind/tests/test_integration_live.py`) for Memgraph, Neo4j, and Redis, introduced a pytest marker configuration, and documented the workflow across README/SETUP/docs.
- Generated a fresh `uv.lock`, pinned `.python-version` to 3.12, and updated install docs to standardise on `uv sync --all-extras`.
- Created `scripts/generate_synthetic_dataset.py` for large JSONL/CSV corpora and referenced it across benchmarking docs.
- Documented the synthetic dataset ingestion workflow across `docs/retrieval.md`, `docs/operations.md`, README, and supporting planning guides so benchmarks can load corpora without recomputing embeddings.
- Updated documentation and planning collateral (README.md, SETUP.md, docs/development.md, docs/testing.md, docs/operations.md, PROJECT.md, PLAN.md, RECOMMENDATIONS.md, ROADMAP.md, ENVIRONMENT_NEEDS.md, NEEDED_FOR_TESTING.md, SOT.md, PLANNING_THOUGHTS.md, DUMMIES.md, TODO.md, RESUME_NOTES.md) to reflect the integration workflow, dataset generation, and the new Pydantic policy.

## Environment State

- Docker Compose is available; starting the stack locally (`docker compose up -d`) allows integration tests (`pytest -m integration`) to hit live Memgraph/Neo4j/Redis instances.
- Internet access is currently enabled and optional packages have been installed via `uv sync`. Keep the network open so dependency locks and maintenance scripts remain functional.
- Changelog entries must continue using Eastern time with timezone codes; remember to update `CHANGELOG.md` after every batch of changes.

## Next Session Starting Points

1. Address remaining `TODO.md` priority items (backend-native vector similarity, Celery worker integration, grpcurl end-to-end tests) now that graph services are accessible locally.
2. Automate the integration suite in CI and capture resource requirements for shared infrastructure.
3. Prepare grpcurl-based smoke tests for `meshmind serve-grpc` and plan protobuf client packaging once integration coverage extends beyond the Python stub.
4. Feed findings from large synthetic datasets into retry/backoff defaults and document recommended values in `ENVIRONMENT_NEEDS.md`, validating the new ingestion workflow as part of those runs.
5. Continue tracking shim retirements in `DUMMIES.md` and follow the cleanup plan in `CLEANUP.md` so remaining fakes can be removed when infrastructure allows.
