# Changelog

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
