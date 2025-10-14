# TODO

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
 - [x] Promote NEW_README.md, archive legacy README, and maintain SOT diagrams and maps.

## Later

- [ ] Harden Celery maintenance tasks to initialize drivers lazily and persist consolidation results.
- [ ] Replace constant importance scoring with a data-driven or LLM-assisted heuristic.
- [ ] Create a fake memgraph driver for testing purposes.
- [ ] Create fake REDIS and Embedding model drivers for testing purposes.
