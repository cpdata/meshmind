# Plan of Action

## Phase 1 – Stabilize Runtime Basics ✅
1. **Dependency Guards** – Implemented lazy driver factories, optional imports, and clear ImportErrors for missing packages.
2. **Default Encoder Registration** – Bootstraps register encoders/entities automatically and the CLI invokes them on startup.
3. **OpenAI SDK Compatibility** – Extraction and embedding adapters align with the Responses API; remaining polish tracked in
   `ISSUES.md`.
4. **Configuration Clarity** – `README_LATEST.md` and `NEEDED_FOR_TESTING.md` document environment variables and service setup.

## Phase 2 – Restore Promised API Surface ✅
1. **Entity & Predicate Registry Wiring** – `MeshMind` now boots registries and storage persists predicates automatically.
2. **CRUD & Triplet Support** – CRUD helpers and triplet APIs live on `MeshMind` and `MemoryManager`, storing relationships via
   `GraphDriver.upsert_edge`.
3. **Relationship-Aware Examples** – Updated example script demonstrates triplet creation and retrieval flows.

## Phase 3 – Retrieval & Maintenance Enhancements (In Progress)
1. **Search Coverage** – Hybrid, vector-only, regex, exact-match, fuzzy, and LLM rerank helpers are implemented and exposed.
   Next: wire graph-backed retrieval queries once Memgraph search endpoints are available.
2. **Maintenance Tasks** – Tasks initialize lazily but still return in-memory results. Persist consolidation outputs and improve
   logging.
3. **Importance Scoring Improvements** – Placeholder scoring remains; design data-driven or LLM-assisted heuristics.

## Phase 4 – Developer Experience & Tooling (In Progress)
1. **Testing Overhaul** – Pytest suites rely on local fixtures with no external services. Extend coverage for Celery workflows
   and graph-backed retrieval once implemented.
2. **Automation & CI** – Makefile provides lint/format/type/test targets and CI runs fmt-check + pytest. Add caching and matrix
   builds when dependencies stabilize.
3. **Environment Provisioning** – Documented manual setup in `NEEDED_FOR_TESTING.md`. Next step: ship docker-compose services
   or scripts for Memgraph and Redis.

## Phase 5 – Strategic Enhancements (Planned)
1. **Pluggable Storage Backends** – Design in-memory/Neo4j drivers that satisfy `GraphDriver` for easier local development.
2. **Service Interfaces** – Build REST/gRPC surfaces for ingestion and retrieval to support remote agents.
3. **Operational Observability** – Layer structured logging, metrics, and dashboards across pipelines and Celery tasks.
4. **Onboarding & Documentation** – Promote the updated README stack, maintain SOT diagrams, and provide troubleshooting guides.
