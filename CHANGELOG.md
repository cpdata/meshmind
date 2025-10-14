# Changelog

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
