# TODO

## Completed

- [x] Implement dependency guards and lazy imports for optional packages (`mgclient`, `tiktoken`, `celery`, `sentence-transformers`).
- [x] Add bootstrap helper for default encoder registration and call it from the CLI.
- [x] Update OpenAI encoder implementation to align with latest SDK responses and retry semantics.
- [x] Improve configuration guidance and automation for environment variables and service setup.
- [x] Wire `EntityRegistry` and `PredicateRegistry` into the storage pipeline and client.
- [x] Implement CRUD and triplet methods on `MeshMind`, including relationship persistence in `GraphDriver`.
- [x] Refresh examples to cover relationship-aware ingestion and retrieval flows.
- [x] Extend retrieval module with vector-only, regex, exact-match, and optional LLM rerank search helpers.
- [x] Modernize pytest suites and add fixtures to run without external services.
- [x] Expand Makefile and add CI workflows for linting, testing, and type checks.
- [x] Document or provision local Memgraph and Redis services (e.g., via docker-compose) for onboarding.
- [x] Abstract `GraphDriver` to support alternative storage backends (Neo4j, in-memory, SQLite prototype).
- [x] Add service interfaces (REST/gRPC) for ingestion and retrieval.
- [x] Introduce observability (logging, metrics) for ingestion and maintenance pipelines.
- [x] Promote the new README, archive the legacy version, and keep SOT diagrams/maps in sync.
- [x] Harden Celery maintenance tasks to initialize drivers lazily and persist consolidation results.
- [x] Replace constant importance scoring with a heuristic driven by token diversity, recency, metadata richness, and embedding magnitude.
- [x] Create fake Memgraph, Redis, and embedding drivers for testing purposes.

## Priority Tasks

- [x] Align the declared Python support with dependency compatibility (document the 3.11/3.12 recommendation and revisit the 3.13 marker in `pyproject.toml`).
- [ ] Document Neo4j driver requirements and validate connectivity against a live cluster.
- [ ] Push graph-backed retrieval queries deeper into Memgraph/Neo4j backends so search executes without materializing entire namespaces.
- [ ] Validate consolidation heuristics on larger datasets and define conflict-resolution/backoff strategies for maintenance writes.
- [ ] Establish evaluation loops (analytics or LLM-assisted) to tune the new importance heuristic over time.
- [x] Expose administrative APIs/CLI commands for predicate registry management and maintenance statistics.
- [ ] Replace the compatibility shim with production Pydantic models once upstream packaging supports the target Python versions.
