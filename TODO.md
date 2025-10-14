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
- [x] Expand `GraphDriver.list_entities` to support namespace/entity-label filters and propagate the behaviour through `MemoryManager`, graph retrieval wrappers, and the MeshMind client.
- [x] Extend REST/gRPC payloads, CLI helpers, and pytest coverage to exercise the new entity-label filtering semantics.
- [x] Stand up `docs/` wiki pages, `ENVIRONMENT_NEEDS.md`, and `RESUME_NOTES.md` so documentation and session hand-off stay current.
- [x] Add unit tests covering namespace/entity-label filtering for the SQLite driver and fake drivers.
- [x] Update the example pipeline (`examples/extract_preprocess_store_example.py`) to demonstrate entity-label restricted retrieval via the MeshMind client.
- [x] Document REST/gRPC request samples that include `entity_labels` in `docs/api.md`.
- [x] Add a regression test confirming `MeshMind.list_memories` forwards `entity_labels` to the memory manager.
- [x] Push graph-backed retrieval queries deeper into Memgraph/Neo4j backends so search executes without materializing entire namespaces.
- [x] Implement pagination/streaming options in `MemoryManager.list_memories` to avoid loading entire namespaces into memory.
- [x] Add CLI/admin command to report memory counts grouped by namespace and entity label for quick health checks.
- [x] Create developer tooling (pre-commit or CI check) that ensures `docs/` pages are touched when code under corresponding modules changes.
- [x] Draft a troubleshooting section documenting optional tooling installation failures (ruff, pyright, typeguard, toml-sort, yamllint) and recommended fallbacks.
- [x] Expose `memory_counts` via the gRPC stub to keep service interfaces aligned.

## Priority Tasks

- [ ] Validate Neo4j driver requirements and connectivity against a live cluster (exercise CLI admin checks end-to-end).
- [ ] Validate consolidation heuristics on larger datasets and define conflict-resolution/backoff strategies for maintenance writes.
- [ ] Establish evaluation loops (analytics or LLM-assisted) to tune the new importance heuristic over time.
- [ ] Replace the compatibility shim with production Pydantic models once upstream packaging supports the target Python versions.
- [ ] Verify curl/grpcurl snippets against running REST/gRPC services once infrastructure is available.
- [ ] Create automated smoke tests for REST `/memories/counts` and `meshmind admin counts` against a live backend when infrastructure is ready.
- [ ] Add gRPC proto definitions and generated clients so the Python stubs align with production servers (including `MemoryCounts`).
- [ ] Benchmark driver-side pagination/filtering on large datasets to tune default candidate limits and document recommended overrides.
- [ ] Implement backend-native vector similarity queries for Memgraph/Neo4j to eliminate Python-side scoring when embeddings are present.
- [ ] Expand the docs guard mapping/tests to cover examples and ensure module-to-doc coverage stays synchronized.

## Recommended Waiting for Approval Tasks

- [ ] Provision Neo4j, Memgraph, and Redis instances accessible from the development environment to unblock live integration tests (requires infrastructure approval).
- [ ] Approve installation of optional dependencies (`neo4j`, `mgclient`, `redis`, `celery`, `tiktoken`, `sentence-transformers`) across CI and developer machines to exercise full workflows.
- [ ] Source or generate large synthetic datasets for consolidation and retrieval benchmarking to validate heuristics under load.
- [ ] Define a policy for reintroducing Pydantic models (version targets, rollout timeline) so compatibility shims can be retired once approved.
