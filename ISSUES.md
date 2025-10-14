# Issues Checklist

## Blockers
- [ ] MeshMind client fails without `mgclient`; introduce lazy driver initialization or documented in-memory fallback.
- [ ] Register a default embedding encoder (OpenAI or sentence-transformers) during startup so extraction and hybrid search can run.
- [ ] Update OpenAI integration to match the current SDK (Responses API payload, embeddings API response structure).
- [ ] Replace eager `tiktoken` imports in `meshmind.core.utils` and `meshmind.pipeline.compress` with guarded, optional imports.
- [ ] Align declared Python requirement with supported dependencies (currently set to Python 3.13 despite ecosystem gaps).

## High Priority
- [x] Implement relationship persistence (`GraphDriver.upsert_edge`) within the storage pipeline and expose triplet APIs.
- [x] Restore high-level API methods promised in README (`register_entity`, predicate management, `add_memory`, `update_memory`, `delete_memory`).
- [x] Ensure CLI ingestion registers entity models and embedding encoders or fails fast with actionable messaging.
- [x] Provide configuration documentation and examples for Memgraph, Redis, and OpenAI environment variables.
- [x] Add automated tests or smoke checks that run without external services (mock OpenAI, stub Memgraph driver).
- [ ] Create real docker-compose services for Memgraph and Redis or remove the placeholder file.

## Medium Priority
- [ ] Persist results from consolidation and compression tasks back to the database (currently in-memory only).
- [ ] Refine `Memory.importance` scoring to reflect actual ranking heuristics instead of a constant.
- [x] Add vector, regex, and exact-match search helpers to match stated feature set or update documentation to demote them.
- [ ] Harden Celery tasks to initialize dependencies lazily and log failures when the driver is unavailable. (In progress: lazy driver initialization added, persistence pending)
- [ ] Reconcile tests that depend on `Memory.pre_init` and outdated OpenAI interfaces with the current implementation.
- [x] Add linting, formatting, and type-checking tooling to improve code quality.

## Low Priority / Nice to Have
- [ ] Offer alternative storage backends (in-memory driver, SQLite, etc.) for easier local development.
- [ ] Provide an administrative dashboard or CLI commands for listing namespaces, counts, and maintenance statistics.
- [ ] Publish onboarding guides and troubleshooting FAQs for contributors.
- [ ] Explore plugin registration for embeddings and retrieval strategies to reduce manual wiring.
