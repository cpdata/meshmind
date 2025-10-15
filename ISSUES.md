# Issues Checklist

## Blockers
- [x] MeshMind client fails without the `mgclient` module; introduce lazy driver initialization or documented in-memory fallback.
- [x] Register a default embedding encoder (OpenAI or sentence-transformers) during startup so extraction and hybrid search can run.
- [x] Update OpenAI integration to match the current SDK (Responses API payload, embeddings API response structure).
- [x] Replace eager `tiktoken` imports in `meshmind.core.utils` and `meshmind.pipeline.compress` with guarded, optional imports.
- [x] Align declared Python requirement with supported dependencies (project now pins Python >=3.11,<3.13).

- [ ] Maintain pip/uv package download access (confirmed working on 2025-10-15) so dependency lock regeneration can proceed reliably across sessions.
## High Priority
- [x] Provide configuration documentation and examples for Memgraph, Redis, and OpenAI environment variables.
- [x] Add automated tests or smoke checks that run without external services (mock OpenAI, stub Memgraph driver).
- [x] Create real docker-compose services for Memgraph and Redis or remove the placeholder file.
- [x] Centralize LLM provider usage behind a configurable client wrapper to remove direct `openai` imports scattered through the codebase.
- [x] Surface LLM override fields via REST/gRPC payloads and integration tests so service clients can select providers/models like the CLI.
- [ ] Document Neo4j driver requirements and verify connectivity against a live cluster (CLI connectivity checks exist but still need validation against a real instance).
- [ ] Exercise the new namespace/entity-label filtering against live Memgraph/Neo4j datasets to confirm Cypher predicates behave as expected.
- [ ] Regenerate `uv.lock` to reflect the updated dependency set (`pymgclient`, `fastapi`, `uvicorn`, extras) so CI tooling stays in sync.
- [x] Break down the competitive roadmap (MCP parity, multi-level scoping, bi-temporal edges, advanced rerankers, governance) into executable epics with owners and timelines referencing `GOALS.md`/`ROADMAP.md` (`ROADMAP_TASKS.md` now captures atomic work including MCP search parity, chat-store compatibility, crew scopes, summaries, and embedder routing).
## Medium Priority
- [x] Persist results from consolidation and compression tasks back to the database (currently in-memory only).
- [x] Refine `Memory.importance` scoring to reflect actual ranking heuristics instead of a constant.
- [x] Add vector, regex, and exact-match search helpers to match stated feature set or update documentation to demote them.
- [x] Harden Celery tasks to initialize dependencies lazily and log failures when the driver is unavailable.
- [ ] Validate consolidation heuristics on larger datasets to measure ranking accuracy and resource usage.
- [ ] Document a conflict-resolution/backoff strategy for consolidation when merged metadata conflicts.
- [ ] Revisit the compatibility shim once production environments support Pydantic 2.x so the real models can be restored.
- [ ] Push graph-backed retrieval into Memgraph/Neo4j search capabilities once available (current wrappers now filter/paginate server-side but still score vectors in Python).
- [ ] Reconcile tests that depend on `Memory.pre_init` and outdated OpenAI interfaces with the current implementation.
- [x] Expose `memory_counts` via a gRPC endpoint to keep service interfaces aligned.
- [x] Add linting, formatting, and type-checking tooling to improve code quality.

- [ ] Validate the new Docker Compose stacks (root and `meshmind/tests/docker/`) on an environment with container support and document host requirements (ports, resources).
## Low Priority / Nice to Have
- [x] Offer alternative storage backends (in-memory driver, SQLite, etc.) for easier local development.
- [x] Provide an administrative dashboard or CLI commands for listing namespaces, counts, and maintenance statistics (CLI admin subcommands now expose predicates, telemetry, and graph checks).
- [ ] Publish onboarding guides and troubleshooting FAQs for contributors.
- [ ] Explore plugin registration for embeddings and retrieval strategies to reduce manual wiring.
