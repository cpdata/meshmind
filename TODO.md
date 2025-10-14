# TODO

- [x] Implement dependency guards and lazy imports for optional packages (`mgclient`, `tiktoken`, `celery`, `sentence-transformers`).
- [x] Add bootstrap helper for default encoder registration and call it from the CLI.
- [x] Update OpenAI encoder implementation to align with latest SDK responses and retry semantics.
- [x] Improve configuration guidance and automation for environment variables and service setup.
- [x] Wire `EntityRegistry` and `PredicateRegistry` into the storage pipeline and client.
- [x] Implement CRUD and triplet methods on `MeshMind`, including relationship persistence in `GraphDriver`.
- [ ] Refresh examples to cover relationship-aware ingestion and retrieval flows.
- [ ] Extend retrieval module with vector-only, regex, exact-match, and optional LLM rerank search helpers.
- [ ] Harden Celery maintenance tasks to initialize drivers lazily and persist consolidation results.
- [ ] Replace constant importance scoring with a data-driven or LLM-assisted heuristic.
- [ ] Modernize pytest suites and add fixtures to run without external services.
- [ ] Expand Makefile and add CI workflows for linting, testing, and type checks.
- [ ] Document or provision local Memgraph and Redis services (e.g., via docker-compose) for onboarding.
- [ ] Abstract `GraphDriver` to support alternative storage backends (Neo4j, in-memory, SQLite prototype).
- [ ] Add service interfaces (REST/gRPC) for ingestion and retrieval.
- [ ] Introduce observability (logging, metrics) for ingestion and maintenance pipelines.
- [ ] Promote NEW_README.md, archive legacy README, and maintain SOT diagrams and maps.
