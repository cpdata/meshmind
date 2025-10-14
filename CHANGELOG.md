# Changelog

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
