# Plan of Action

## Phase 1 – Stabilize Runtime Basics
1. **Dependency Guards**
   - Add lazy imports and feature flags for `mgclient`, `tiktoken`, `celery`, and `sentence-transformers` so missing packages do not crash the import path.
   - Provide clear error messages and documentation when dependencies are absent.
2. **Default Encoder Registration**
   - Introduce a bootstrap helper that registers an OpenAI encoder (or configurable fallback) on package import or via CLI option.
   - Update CLI to call the bootstrap helper before extraction.
3. **OpenAI SDK Compatibility**
   - Refactor `OpenAIEmbeddingEncoder` and pipeline extraction to use the latest `openai` SDK response objects with proper retry and error handling.
4. **Configuration Clarity**
   - Publish a setup guide covering environment variables, Memgraph/Redis provisioning, and CLI usage.

## Phase 2 – Restore Promised API Surface
1. **Entity & Predicate Registry Wiring**
   - Connect `EntityRegistry` and `PredicateRegistry` to `MeshMind`, ensuring registered models and predicates persist to the database.
2. **CRUD & Triplet Support**
   - Add `add_memory`, `update_memory`, `delete_memory`, `register_entity`, `register_allowed_predicates`, and `add_triplet` methods on `MeshMind` that wrap pipeline + driver operations.
   - Extend storage pipeline to create relationships via `GraphDriver.upsert_edge` with sensible defaults for subject/object resolution.
3. **Relationship-Aware Examples**
   - Update example scripts and documentation to demonstrate triplet storage and retrieval once implemented.

## Phase 3 – Retrieval & Maintenance Enhancements
1. **Search Coverage**
   - Implement vector-only, regex, and exact-match search helpers and expose them through `meshmind.retrieval.search`.
   - Optionally integrate LLM reranking for high-quality results.
2. **Maintenance Tasks**
   - Ensure consolidation and compression tasks persist results back to Memgraph.
   - Move Celery driver initialization into task functions to avoid import-time failures and add logging for missing dependencies.
3. **Importance Scoring Improvements**
   - Replace the constant importance score with a heuristic or LLM-based evaluator aligned with README claims.

## Phase 4 – Developer Experience & Tooling
1. **Testing Overhaul**
   - Modernize pytest suites to align with new SDKs, provide fixtures for stub drivers, and ensure tests run without external services.
   - Add coverage for new API methods and relationship handling.
2. **Automation & CI**
   - Expand the Makefile with lint, format, test, and type-check targets.
   - Configure CI (GitHub Actions or similar) to run the suite and static checks on push/PR.
3. **Environment Provisioning**
   - Replace `docker-compose.yml` with services for Memgraph and Redis or document alternative local development setups.

## Phase 5 – Strategic Enhancements
1. **Pluggable Storage Backends**
   - Abstract `GraphDriver` further to support alternative backends (Neo4j, in-memory driver, SQLite prototype).
2. **Service Interfaces**
   - Expose REST/gRPC endpoints for ingestion and retrieval to enable external integrations.
3. **Operational Observability**
   - Add logging, metrics, and dashboards for maintenance jobs, ingestion throughput, and retrieval latency.
4. **Onboarding & Documentation**
   - Promote `NEW_README.md` to `README.md`, archive the legacy document, and maintain `SOT.md` with diagrams and workflow maps.
