# Issues Checklist

## Blockers
- [x] MeshMind client fails without `mgclient`; introduce lazy driver initialization or documented in-memory fallback.
- [x] Register a default embedding encoder (OpenAI or sentence-transformers) during startup so extraction and hybrid search can run.
- [x] Update OpenAI integration to match the current SDK (Responses API payload, embeddings API response structure).
- [x] Replace eager `tiktoken` imports in `meshmind.core.utils` and `meshmind.pipeline.compress` with guarded, optional imports.
- [x] Align declared Python requirement with supported dependencies (project now pins Python >=3.11,<3.13).

## High Priority
- [x] Implement relationship persistence (`GraphDriver.upsert_edge`) within the storage pipeline and expose triplet APIs.
- [x] Restore high-level API methods promised in README (`register_entity`, predicate management, `add_memory`, `update_memory`, `delete_memory`).
- [x] Ensure CLI ingestion registers entity models and embedding encoders or fails fast with actionable messaging.
- [x] Provide configuration documentation and examples for Memgraph, Redis, and OpenAI environment variables.
- [x] Add automated tests or smoke checks that run without external services (mock OpenAI, stub Memgraph driver).
- [x] Create real docker-compose services for Memgraph and Redis or remove the placeholder file.
- [ ] Document Neo4j driver requirements and verify connectivity against a live cluster (CLI connectivity checks exist but still need validation against a real instance).
- [ ] Exercise the new namespace/entity-label filtering against live Memgraph/Neo4j datasets to confirm Cypher predicates behave as expected.

## Medium Priority
- [x] Persist results from consolidation and compression tasks back to the database (currently in-memory only).
- [x] Refine `Memory.importance` scoring to reflect actual ranking heuristics instead of a constant.
- [x] Add vector, regex, and exact-match search helpers to match stated feature set or update documentation to demote them.
- [x] Harden Celery tasks to initialize dependencies lazily and log failures when the driver is unavailable.
- [ ] Validate consolidation heuristics on larger datasets and add conflict-resolution strategy when merged metadata conflicts.
- [ ] Revisit the compatibility shim once production environments support Pydantic 2.x so the real models can be restored.
- [ ] Push graph-backed retrieval into Memgraph/Neo4j search capabilities once available (current wrappers now filter/paginate server-side but still score vectors in Python).
- [ ] Reconcile tests that depend on `Memory.pre_init` and outdated OpenAI interfaces with the current implementation.
- [x] Expose `memory_counts` via a gRPC endpoint to keep service interfaces aligned.
- [x] Add linting, formatting, and type-checking tooling to improve code quality.

## Low Priority / Nice to Have
- [x] Offer alternative storage backends (in-memory driver, SQLite, etc.) for easier local development.
- [x] Provide an administrative dashboard or CLI commands for listing namespaces, counts, and maintenance statistics (CLI admin subcommands now expose predicates, telemetry, and graph checks).
- [ ] Publish onboarding guides and troubleshooting FAQs for contributors.
- [ ] Explore plugin registration for embeddings and retrieval strategies to reduce manual wiring.
