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
   Next: wire graph-backed retrieval queries once Memgraph/Neo4j search endpoints are available.
2. **Maintenance Tasks** – Tasks now emit telemetry but still return in-memory results. Persist consolidation outputs and improve
   failure handling.
3. **Importance Scoring Improvements** – Placeholder scoring remains; design data-driven or LLM-assisted heuristics.

## Phase 4 – Developer Experience & Tooling (In Progress)
1. **Testing Overhaul** – Pytest suites rely on local fixtures with no external services. Extend coverage for Celery workflows
   and graph-backed retrieval once implemented.
2. **Automation & CI** – Makefile provides lint/format/type/test targets and CI runs fmt-check + pytest. Add caching and matrix
   builds when dependencies stabilize.
3. **Environment Provisioning** – Docker Compose now provisions Memgraph, Redis, and a Celery worker. Track multi-backend
   examples and ensure documentation stays current.

## Phase 5 – Strategic Enhancements (Planned)
1. **Graph-Backed Retrieval** – Push search workloads into the configured graph driver once backend capabilities land.
2. **Operational Observability** – Export telemetry to Prometheus/OpenTelemetry and surface dashboards/alerts.
3. **Celery Hardening** – Persist consolidation/compression outputs back into the graph and add retry policies.
4. **Importance Scoring** – Replace constant heuristics with data-driven scoring or LLM evaluation workflows.
