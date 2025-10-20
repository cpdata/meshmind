# Changelog

## [2025-10-20T04:12:44-04:00 (America/New_York)]
### Added
- Introduced `.beads/` project database and exported Beads issue JSONL by initializing bd and migrating existing TODO items.
- Added `reference-docs/` snapshots of upstream Beads documentation (`Beads-*.md`) for local reference.

### Changed
- Rewrote `AGENTS.md` to mandate Beads-based workflow and appended the `bd quickstart` reference output; simplified `TODO.md` to delegate planning to bd.
- Imported every task from the legacy `TODO.md` into the Beads tracker with appropriate open/closed status and added an `ISSUES.md` note pointing contributors to bd commands.

## [2025-10-16T20:39:06-04:00 (America/New_York)]
### Added
- Added live integration coverage for Memgraph, Neo4j, and Redis via `meshmind/tests/test_integration_live.py` and configured
  pytest markers/default options in `pyproject.toml` so `pytest -m integration` exercises the docker-compose stack.
- Introduced `scripts/generate_synthetic_dataset.py` to produce large JSONL/CSV corpora (defaults: 10k memories, 20k triplets,
  384-dim embeddings) for benchmarking and load testing.

### Changed
- Regenerated `uv.lock`, pinned `.python-version` to 3.12, and updated installation guidance (`README.md`, `SETUP.md`,
  `docs/development.md`, `docs/testing.md`, `docs/operations.md`, `ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`) to standardise on
  `uv sync --all-extras` and document the new Pydantic 2.x policy.
- Refreshed planning and status collateral (`PROJECT.md`, `PLAN.md`, `SOT.md`, `ROADMAP.md`, `PLANNING_THOUGHTS.md`,
  `RECOMMENDATIONS.md`, `RESUME_NOTES.md`, `DUMMIES.md`, `TODO.md`, `ISSUES.md`) to reflect integration workflows, dataset
  generation guidance, and completed approval tasks.
## [2025-10-16T16:35:00-04:00 (America/New_York)]
### Added
- Added a `serve-grpc` CLI subcommand (`meshmind/cli/__main__.py`) that instantiates
  `MemoryService` via `create_graph_driver`, delegates to
  `meshmind.api.grpc_server.serve_forever`, and is exercised by
  `meshmind/tests/test_cli_admin.py` alongside the new docker-compose service
  definitions (`docker-compose.yml`, `meshmind/tests/docker/full-stack.yml`).
- Recorded CLI runtime coverage and protobuf drift checks by extending
  `meshmind/tests/test_cli_admin.py` and `meshmind/tests/test_protos_packaging.py`,
  ensuring the new `serve-grpc` command and `scripts/check_protos.py` guard remain
  functional.

### Changed
- Removed the legacy REST stub and Celery fallbacks by requiring real FastAPI and
  Celery imports (`meshmind/api/rest.py`, `meshmind/tasks/celery_app.py`,
  `meshmind/tasks/scheduled.py`) and updated smoke tests to exercise the FastAPI
  app via `fastapi.testclient.TestClient` (`meshmind/tests/test_service_interfaces.py`,
  `meshmind/tests/test_counts_smoke.py`).
- Hardened protobuf utilities (`scripts/generate_protos.py`, `scripts/check_protos.py`)
  to normalise relative imports so package builds remain import-safe.
- Updated provisioning assets and documentation (README.md, SETUP.md,
  docs/api.md, docs/operations.md, docs/testing.md, PROJECT.md, PLAN.md,
  RECOMMENDATIONS.md, FINDINGS.md, ROADMAP.md, DUMMIES.md, CLEANUP.md,
  ENVIRONMENT_NEEDS.md, NEEDED_FOR_TESTING.md, SOT.md, TODO.md, RESUME_NOTES.md)
  to describe the new gRPC workflow, retired shims, and compose stacks.
- Expanded the documentation guard mapping (`scripts/check_docs_sync.py`) so CLI
  changes require updates to the API/operations guides.

## [2025-10-16T12:06:05-04:00 (America/New_York)]
### Added
- Introduced `meshmind/api/grpc_server.py` with `create_server`, `serve`, and `serve_forever` helpers so production deployments
  can expose the canonical gRPC service via `grpc.aio` without rolling bespoke glue code.
- Added runtime coverage in `meshmind/tests/test_grpc_runtime.py` that ingests/searches over a live channel and asserts graceful
  cancellation, plus `meshmind/tests/test_protos_packaging.py` to guarantee the proto ships with the distribution.
- Created `scripts/generate_protos.py` and `scripts/check_protos.py` alongside Makefile targets (`protos`, `protos-check`) and a
  GitHub Actions step so protobuf drift is caught automatically; CI now installs the tooling with `uv --system` and runs the
  verification command.

### Changed
- Updated documentation (`README.md`, `SETUP.md`, `docs/api.md`, `docs/operations.md`, `docs/testing.md`, `docs/development.md`,
  `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`, `ISSUES.md`, `SOT.md`, `ROADMAP.md`, `DUMMIES.md`,
  `ENVIRONMENT_NEEDS.md`, `RESUME_NOTES.md`, `TODO.md`) to describe the new gRPC runtime workflow, follow-up tasks (CLI entry
  point, docker-compose service), and proto maintenance process.
- Refreshed automation assets: `Makefile` now exposes `protos`/`protos-check`, `.github/workflows/ci.yml` invokes the new target
  during linting, and `docs/testing.md` enumerates the additional runtime/packaging tests.

## [2025-10-16T05:12:43-04:00 (America/New_York)]
### Added
- Authored `meshmind/protos/memory_service.proto` and generated `memory_service_pb2(_grpc).py`, exposing helpers in `meshmind.api.grpc`
  so the gRPC surface now shares a canonical protobuf schema.
- Introduced `meshmind/protos/__init__.py` with a `data_path()` helper and configured `pyproject.toml` to ship `.proto` files with the
  package.
- Added a `make benchmarks` target that executes `scripts/evaluate_importance.py`, `scripts/consolidation_benchmark.py`, and
  `scripts/benchmark_pagination.py`, writing JSON snapshots to `build/benchmarks/` for quick regressions.

### Changed
- Refactored `meshmind/api/grpc.py` to map protobuf messages to `MemoryPayload`/`TripletPayload`, ensuring search results preserve
  timestamps and metadata while keeping convenience helpers for tests.
- Updated gRPC-related tests and docs (`meshmind/tests/test_service_interfaces.py`, `meshmind/tests/test_api_examples.py`,
  `docs/api.md`, `README.md`, `docs/testing.md`, `docs/operations.md`, `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`,
  `SOT.md`, `ROADMAP.md`, `ISSUES.md`, `RESUME_NOTES.md`, `DUMMIES.md`, `CLEANUP.md`, `ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`,
  `TODO.md`) to reference the protobuf-backed interface and new benchmarking workflow.
- Declared `grpcio`, `grpcio-tools`, and `protobuf` as first-class dependencies (including the testing extra) and ensured setup scripts
  continue validating optional packages.

### Fixed
- Ensured generated protobuf files are packaged by default via `[tool.setuptools.package-data]`, preventing downstream installs from
  missing the canonical schema.

## [2025-10-16T04:52:41-04:00 (America/New_York)]
### Added
- Introduced benchmarking and evaluation tooling: `scripts/evaluate_importance.py` for heuristic summaries, `scripts/consolidation_benchmark.py` for consolidation throughput, and `scripts/benchmark_pagination.py` for driver pagination measurements, each covered by pytest (`meshmind/tests/test_benchmark_scripts.py`).
- Added REST/gRPC documentation smoke tests in `meshmind/tests/test_api_examples.py` to validate the new curl/grpcurl snippets against the FastAPI app and gRPC stub.

### Changed
- Extended `meshmind/cli/admin.py` and `meshmind/tests/test_cli_admin.py` with `--max-attempts`, `--base-delay`, and `--run` overrides so maintenance retries can be tuned per invocation.
- Expanded consolidation coverage via `meshmind/tests/test_pipeline_preprocess_store.py` to exercise large synthetic datasets and ensure summaries/importance survive batching.
- Updated project documentation (`README.md`, `docs/api.md`, `docs/operations.md`, `SOT.md`, `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`, `ISSUES.md`, `ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`, `RESUME_NOTES.md`, `TODO.md`, `DUMMIES.md`, `CLEANUP.md`) to describe the CLI overrides, benchmarking utilities, shim retirement, and refreshed backlog priorities.

### Removed
- Retired the Pydantic compatibility layer by deleting `meshmind/_compat/pydantic.py`, updating all imports to use first-party Pydantic models, and pruning `_compat` from the repository map.

## [2025-10-14T22:51:20-04:00 (America/New_York)]
### Changed
- Documented LLM override precedence in `README.md`, expanded service documentation in `docs/api.md` and
  `docs/configuration.md`, and clarified CLI guidance so per-request model/endpoint overrides are discoverable.
- Updated provisioning guidance in `SETUP.md` and `docs/operations.md` to describe the validation/dry-run flags in
  `run/install_setup.sh` and `run/maintenance_setup.sh`, aligning with the new pytest smoke tests.
- Refreshed planning artifacts (`SOT.md`, `PLAN.md`, `PROJECT.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`, `ISSUES.md`, `TODO.md`)
  to capture timezone-aware timestamp defaults, FakeLLMClient coverage, and the completed documentation tasks.
- Synced testing references by elaborating on the FakeLLMClient behaviour in `docs/testing.md`, extending `DUMMIES.md`, and
  updating environment guides (`ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`) to note optional packages now install with
  network access.
- Revised `RESUME_NOTES.md` with the latest documentation work and remaining priorities to aid the next development session.

## [2025-10-14T20:40:15-04:00 (America/New_York)]
### Added
- Introduced `meshmind/llm_client.py` with `LLMConfig`, a cached OpenAI-compatible `LLMClient`, and builders that hydrate
  per-operation defaults from `LLM_*` environment variables so extraction, embeddings, and reranking share a single
  provider abstraction.
- Added `meshmind/tests/test_llm_client.py` to verify configuration overrides and client caching behaviour without
  requiring the real SDK.
- Authored `CLEANUP.md` to track post-restriction remediation work for compatibility shims now that full dependencies are
  installable.

### Changed
- Refactored `meshmind.client.MeshMind`, `meshmind/core/embeddings.py`, `meshmind/pipeline/extract.py`, and
  `meshmind/retrieval/rerank.py` to consume the new `LLMClient`, cascade rerank defaults, and remove direct `openai`
  imports.
- Expanded the CLI ingest command (`meshmind/cli/__main__.py`, `meshmind/cli/ingest.py`) with `--llm-*` flags that override
  per-operation models/endpoints and wire them through to `MeshMind`.
- Updated configuration plumbing (`meshmind/core/config.py`, `scripts/check_docs_sync.py`) so `LLM_*` variables are first-class
  settings and documentation guard checks map the new module to the wiki.
- Refreshed documentation (`README.md`, `docs/configuration.md`, `docs/pipelines.md`, `docs/retrieval.md`, `docs/operations.md`,
  `docs/testing.md`, `docs/troubleshooting.md`, `SETUP.md`, `SOT.md`, `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`,
  `ISSUES.md`, `ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`, `FINDINGS.md`, `RESUME_NOTES.md`) to describe the provider-agnostic
  LLM workflow, new CLI overrides, and related environment variables.
- Extended `TODO.md` and backlog artifacts to mark the LLM wrapper task complete, add follow-up work for surfacing overrides in
  service payloads, and record the new cleanup plan.

## [2025-10-14T19:44:39-04:00 (America/New_York)]
### Added
- Authored `DUMMIES.md` to catalogue compatibility shims (`meshmind/_compat/pydantic.py`), REST/gRPC stubs, Celery fallbacks,
  and fake drivers with guidance on which artifacts to retire versus keep for offline testing.

### Changed
- Updated `README.md`, `SOT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `PROJECT.md`, and `FINDINGS.md` to reference the new
  compatibility inventory so contributors know where to track shim removal work.
## [2025-10-14T16:46:48-04:00 (America/New_York)]
### Changed
- Swapped the Memgraph dependency in `pyproject.toml` from `mgclient` to `pymgclient` and confirmed optional packages install
  cleanly with the refreshed network access (`uv pip install`).
- Updated environment references—`ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`, `SETUP.md`, `README.md`, `README_OLD.md`, `SOT.md`, `PROJECT.md`,
  `FINDINGS.md`, `ISSUES.md`, `TODO.md`, `docs/` wiki pages—to describe `pymgclient` as the Memgraph package while preserving
  the runtime `mgclient` module references.
- Revised `AGENTS.md` to require Eastern Time timestamps with timezone codes for every changelog entry and aligned `RESUME_NOTES.md`
  with the newly installed optional dependencies and confirmed internet availability.

## [2025-10-14T15:53:42-04:00 (America/New_York)]
### Added
- Authored `run/install_setup.sh` and `run/maintenance_setup.sh` bash scripts that install system packages (`build-essential`,
  `cmake`, `libssl-dev`, `libopenblas-dev`, etc.) and synchronize Python dependencies via `uv pip sync` so fresh and cached
  environments can bootstrap optional tooling (`neo4j`, `mgclient`, `redis`, REST extras) once internet access is available.

### Changed
- Updated `AGENTS.md` with an atomic-task requirement and refreshed `TODO.md` to prepend granular items for drafting
  `CLEANUP.md`, introducing a provider-agnostic `meshmind/llm_client.py`, replacing direct OpenAI imports, and wiring cascaded
  LLM overrides across configuration, CLI, API, tests, and documentation.
- Extended planning/backlog documents—`ISSUES.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `SOT.md`, `RESUME_NOTES.md`—to capture the
  upcoming LLM client refactor, dependency sync expectations, and the new automation scripts.
- Added setup guidance in `README.md` and `SETUP.md` pointing to the `run/` scripts so developers with sudo access can
  bootstrap environments automatically.

## [2025-10-17T18:45:00Z]
### Added
- Created a Dockerfile for integration workloads and introduced targeted Compose stacks
  under `meshmind/tests/docker/` (Memgraph, Neo4j, Redis, full-stack) alongside a
  developer-facing provisioning guide in `SETUP.md` to document service bootstrapping
  commands and environment requirements.

### Changed
- Expanded `pyproject.toml` to install optional dependencies (`fastapi`,
  `uvicorn[standard]`, `neo4j`, `mgclient`, `redis`) by default and defined extras
  (`dev`, `docs`, `testing`); updated the `Makefile` `install` target accordingly and
  regenerated setup documentation across `README.md`, `docs/`, `PROJECT.md`, `PLAN.md`,
  `SOT.md`, `NEEDED_FOR_TESTING.md`, `ENVIRONMENT_NEEDS.md`, `FINDINGS.md`,
  `RECOMMENDATIONS.md`, and `RESUME_NOTES.md` to reference the new workflow and
  credentials.
- Reworked the root `docker-compose.yml` to provision Memgraph, Neo4j, and Redis with
  health checks and volumes, added Compose variants in `meshmind/tests/docker/`, and
  refreshed onboarding materials (`SETUP.md`, `README.md`, `docs/configuration.md`,
  `docs/operations.md`, `docs/testing.md`) to call out the new ports, credentials, and
  teardown guidance.
- Replaced references to `pymgclient` with `mgclient` throughout dependency notes and
  environment files to match the updated driver import.

### Fixed
- Patched `meshmind/cli/admin.py` to import `argparse`, restoring CLI admin command
  registration after the module refactor.
- Updated `.github/workflows/ci.yml` to pass `--system` to `uv pip install`, resolving
  the "No virtual environment found" failure during lint/test setup.

## [2025-10-16T18:30:00Z]
### Fixed
- Adjusted `meshmind/tests/test_service_interfaces.py::test_memory_service_ingest_and_search` to return a hydrated `Memory`
  instance from the monkey-patched `list_memories` stub, ensuring pagination-aware search paths remain asserted while avoiding
  empty result sets during verification.

## [2025-10-16T12:00:00Z]
### Added
- Introduced pagination-aware graph access by adding `search_entities` and `count_entities` to every `GraphDriver` implementation, wiring a new `meshmind admin counts` CLI subcommand and REST `/memories/counts` route through `MemoryManager`, `MemoryService`, and the MeshMind client.
- Added `scripts/check_docs_sync.py` plus a Makefile target, CI step, and pytest coverage to guard documentation updates whenever code under mapped modules changes.

### Changed
- Extended `MemoryManager.list_memories`, MeshMind client helpers, retrieval graph wrappers, and service adapters to forward `offset`, `limit`, and `query` hints, delegating filtering to the active driver before in-memory scoring.
- Updated examples and tests (`meshmind/tests/test_db_drivers.py`, `test_service_interfaces.py`, `test_graph_retrieval.py`, `test_cli_admin.py`, `test_client.py`, `test_docs_guard.py`) to cover pagination, counts, and driver-side search semantics.

### Documentation
- Refreshed `README.md`, `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `ISSUES.md`, `SOT.md`, `FINDINGS.md`, `AGENTS.md`, `TODO.md`, and the developer wiki (`docs/api.md`, `docs/development.md`, `docs/operations.md`, `docs/persistence.md`, `docs/retrieval.md`, `docs/troubleshooting.md`) to describe pagination, counts, docs-guard workflows, and updated service interfaces.
## [2025-10-15T15:30:00Z]
### Added
- Created a developer wiki under `docs/` covering architecture, pipelines, persistence, retrieval, configuration, testing, operations, telemetry, and development workflows so code changes stay synchronized with reference material.
- Authored `ENVIRONMENT_NEEDS.md` to request optional dependency installs and external services, plus `RESUME_NOTES.md` for session-to-session continuity.

### Changed
- Expanded the `GraphDriver` contract to accept namespace and entity-label filters when listing entities, updating the in-memory, SQLite, Neo4j, and Memgraph drivers to push filtering into their native query layers.
- Propagated the new filtering through `MemoryManager`, `MeshMind.list_memories`, graph-backed retrieval wrappers, and service interfaces (REST/gRPC), ensuring hybrid searches hydrate only the required entity types.
- Updated tests (`meshmind/tests/test_graph_retrieval.py`, `test_pipeline_preprocess_store.py`, `test_service_interfaces.py`) to cover entity-label filtering across client, REST, and gRPC paths.

### Documentation
- Refreshed `README.md`, `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `ISSUES.md`, `SOT.md`, `DISCREPANCIES.md`, `FINDINGS.md`, `TODO.md`, and `AGENTS.md` to describe the new driver filtering, documentation workflow, environment checklist, and wiki requirements.

## [2025-02-15T00:45:00Z]
### Added
- Introduced `meshmind/retrieval/graph.py` with hybrid/vector/regex/exact/BM25/fuzzy wrappers that hydrate candidates from the active `GraphDriver` before delegating to existing scorers, plus `meshmind/tests/test_graph_retrieval.py` to verify namespace filtering and hybrid integration.
- Added `meshmind/cli/admin.py` and wired `meshmind/cli/__main__.py` to expose `admin` subcommands for predicate management, maintenance telemetry, and graph connectivity checks; created `meshmind/tests/test_cli_admin.py` to cover the new flows.
- Created `meshmind/tests/test_neo4j_driver.py` and a `Neo4jGraphDriver.verify_connectivity` helper to exercise driver-level sanity checks without a live cluster.
- Logged importance score distributions via `meshmind/pipeline/preprocess.summarize_importance` so telemetry captures mean/stddev/recency metrics after scoring.

### Changed
- Updated `MeshMind` search helpers (`meshmind/client.py`) to auto-load memories from the configured driver when `memories` is `None`, reusing the new graph-backed wrappers.
- Reworked `meshmind/pipeline/consolidate.py` to return a `ConsolidationPlan` with batch/backoff thresholds and skipped-group tracking; `meshmind/tasks/scheduled.consolidate_task` now emits skip counts and returns a structured summary.
- Tuned Python compatibility metadata to `>=3.11,<3.13` in `pyproject.toml` and refreshed docs (`README.md`, `NEEDED_FOR_TESTING.md`, `SOT.md`) accordingly.
- Enhanced `meshmind/pipeline/preprocess.py` to emit telemetry gauges for importance scoring and added `meshmind/tests/test_pipeline_preprocess_store.py::test_score_importance_records_metrics`.
- Expanded retrieval, CLI, and driver test coverage (`meshmind/tests/test_retrieval.py`, `meshmind/tests/test_tasks_scheduled.py`) to account for graph-backed defaults and new return types.

### Documentation
- Updated `README.md`, `PROJECT.md`, `PLAN.md`, `SOT.md`, `FINDINGS.md`, `DISCREPANCIES.md`, `RECOMMENDATIONS.md`, `NEEDED_FOR_TESTING.md`, `ISSUES.md`, and `TODO.md` to describe graph-backed retrieval wrappers, CLI admin tooling, consolidation backoff behaviour, telemetry metrics, and revised Python support.
- Copied the refreshed README guidance into `README_OLD.md` as an archival reference while keeping `README.md` as the primary source.

## [2025-10-14T14:57:47Z]
### Added
- Introduced `meshmind/_compat/pydantic.py` to emulate `BaseModel`, `Field`, and `ValidationError` when Pydantic is unavailable, enabling tests to run in constrained environments.
- Added `meshmind/testing/fakes.py` with `FakeMemgraphDriver`, `FakeRedisBroker`, and `FakeEmbeddingEncoder`, plus a package export and dedicated pytest coverage (`meshmind/tests/test_db_drivers.py`, `meshmind/tests/test_tasks_scheduled.py`).
- Created heuristics-focused test cases for consolidation outcomes, maintenance tasks, and the revised retrieval dispatcher to guarantee behaviour without external services.

### Changed
- Replaced the constant importance assignment in `meshmind/pipeline/preprocess.score_importance` with a heuristic that factors token diversity, recency, metadata richness, and embedding magnitude.
- Rebuilt `meshmind/pipeline/consolidate` around a `ConsolidationOutcome` dataclass that merges metadata, averages embeddings, and surfaces removal IDs; `meshmind/tasks/scheduled.consolidate_task` now applies updates and deletes duplicates lazily via `_get_manager`/`_reset_manager` helpers.
- Hardened Celery maintenance tasks by logging driver initialization failures, tracking update counts, and returning deterministic totals; compression counts now reflect the number of persisted updates.
- Updated `meshmind/core/similarity`, `meshmind/retrieval/bm25`, and `meshmind/retrieval/fuzzy` with pure-Python fallbacks so numpy, scikit-learn, and rapidfuzz remain optional.
- Adjusted `meshmind/pipeline/extract.extract_memories` to defer `openai` imports until a default client is required, unblocking DummyLLM-driven tests.
- Reworked `meshmind/retrieval/search.search` to rerank the original (filtered) candidate ordering, prepend reranked results, and append hybrid-sorted fallbacks, preventing index drift when rerankers return relative positions.
- Normalised SQLite entity hydration in `meshmind/db/sqlite_driver._row_to_dict` so JSON metadata is decoded only when stored as strings.
- Refreshed pytest fixtures (`meshmind/tests/conftest.py`, `meshmind/tests/test_pipeline_preprocess_store.py`) to use deterministic encoders and driver doubles, ensuring CRUD and retrieval suites run without live services.

### Documentation
- Promoted `README.md` as the single source of truth (archiving the previous copy in `README_OLD.md`) and documented the new heuristics, compatibility shims, and test doubles.
- Updated `NEEDED_FOR_TESTING.md` with notes about the compatibility layer, optional dependencies, and fake drivers.
- Reconciled `PROJECT.md`, `ISSUES.md`, `PLAN.md`, `SOT.md`, `RECOMMENDATIONS.md`, `DISCREPANCIES.md`, `FINDINGS.md`, `TODO.md`, and `CHANGELOG.md` to capture the new persistence behaviour, heuristics, fallbacks, and remaining roadmap items.

## [Unreleased] - 2025-02-14
### Added
- Configurable graph driver factory with in-memory, SQLite, Memgraph, and optional Neo4j implementations plus supporting tests.
- REST and gRPC service layers (with FastAPI stub fallback) for ingestion and retrieval, including coverage in the test suite.
- Observability utilities that collect metrics and structured logs across pipelines and scheduled Celery tasks.
- Docker Compose definition provisioning Memgraph, Redis, and a Celery worker for local development.
- Vector-only, regex, exact-match, and optional LLM rerank retrieval helpers with reranker utilities and exports.
- MeshMind client wrappers for hybrid, vector, regex, and exact searches plus driver accessors.
- Example script demonstrating triplet storage and diverse retrieval flows.
- Pytest fixtures for encoder and memory factories alongside new retrieval tests that avoid external services.
- Makefile targets for linting, formatting, type checks, and tests, plus a GitHub Actions workflow running lint and pytest.
- README_LATEST.md capturing the current implementation and CHANGELOG.md for release notes.

### Changed
- Settings now surface `GRAPH_BACKEND`, Neo4j, and SQLite options while README/NEEDED_FOR_TESTING document the expanded setup.
- README, README_LATEST, and NEW_README were consolidated so the promoted README reflects current behaviour.
- PROJECT, PLAN, SOT, FINDINGS, DISCREPANCIES, ISSUES, RECOMMENDATIONS, and TODO were refreshed to capture new capabilities and
  re-homed backlog items under a "Later" section.
- Updated `SearchConfig` to support rerank models and refreshed MeshMind documentation across PROJECT, PLAN, SOT, FINDINGS,
  DISCREPANCIES, RECOMMENDATIONS, ISSUES, TODO, and NEEDED_FOR_TESTING files.
- Revised `meshmind.retrieval.search` to apply filters centrally, expose new search helpers, and integrate reranking.
- Exposed graph driver access on MeshMind and refreshed retrieval-facing examples and docs.

### Fixed
- Example ingestion script now uses MeshMind APIs correctly and illustrates relationship persistence.
- Tests rely on fixtures rather than deprecated hooks, improving portability across environments without Memgraph/OpenAI.
## [2025-10-15T18:00:51-04:00 (America/New_York)]
### Added
- Authored strategic documentation (`ROADMAP.md`, `PLANNING_THOUGHTS.md`) and a competitor brief (`research/overview.md`) so planning artifacts capture milestone expectations, architectural questions, and market context alongside the existing SOT.
- Introduced REST/CLI smoke coverage for `/memories/counts` via `meshmind/tests/test_counts_smoke.py`, ensuring the new docs and README examples remain executable with the in-memory driver.

### Changed
- Implemented configurable exponential backoff for consolidation/compression writes by extending `meshmind/core/config.py` with `MAINTENANCE_MAX_ATTEMPTS` / `MAINTENANCE_BASE_DELAY_SECONDS`, updating `meshmind/tasks/scheduled.py` to retry maintenance operations, and expanding `meshmind/tests/test_tasks_scheduled.py` to assert retry success/failure paths.
- Documented the new maintenance controls and telemetry across `README.md`, `docs/configuration.md`, `docs/operations.md`, `docs/telemetry.md`, `docs/testing.md`, `SOT.md`, `PLAN.md`, `PROJECT.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`, `ISSUES.md`, `ENVIRONMENT_NEEDS.md`, and `NEEDED_FOR_TESTING.md`.
- Refreshed `TODO.md`, `RESUME_NOTES.md`, and related planning files to reflect the completed backlog items, highlight remaining priority tasks, and align with the new retry instrumentation.
