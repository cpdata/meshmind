# Plan of Action

## Phase 1 – Stabilize Runtime Basics ✅
1. **Dependency Guards** – Implemented lazy driver factories, optional imports, and clear ImportErrors for missing packages.
2. **Default Encoder Registration** – Bootstraps register encoders/entities automatically and the CLI invokes them on startup.
3. **OpenAI SDK Compatibility** – Extraction and embedding adapters align with the Responses API; remaining polish tracked in
   `ISSUES.md`.
4. **Configuration Clarity** – `README.md`, `ENVIRONMENT_NEEDS.md`, and the new `docs/` pages document environment variables and service setup.

## Phase 2 – Restore Promised API Surface ✅
1. **Entity & Predicate Registry Wiring** – `MeshMind` now boots registries and storage persists predicates automatically.
2. **CRUD & Triplet Support** – CRUD helpers and triplet APIs live on `MeshMind` and `MemoryManager`, storing relationships via
   `GraphDriver.upsert_edge`.
3. **Relationship-Aware Examples** – Updated example script demonstrates triplet creation and retrieval flows.

## Phase 3 – Retrieval & Maintenance Enhancements (In Progress)
1. **Search Coverage** – Hybrid, vector-only, regex, exact-match, fuzzy, and LLM rerank helpers are implemented and exposed.
   Graph-backed wrappers now pull namespace + entity-label filtered candidates from the configured driver when no list is provided. Next: push similarity scoring
   into Memgraph/Neo4j to avoid loading entire namespaces.
2. **Maintenance Tasks** – Tasks emit telemetry and persist consolidation/compression results. Consolidation planning enforces
   batch/backoff thresholds and surfaces skipped groups. Next: validate heuristics on larger datasets and tune the thresholds with
   real data.
3. **Importance Scoring Improvements** – Heuristic scoring is live and now records distribution metrics via telemetry. Next:
   design data-driven evaluation loops or LLM-assisted ranking to tune weights over time.

## Phase 4 – Developer Experience & Tooling (In Progress)
1. **Testing Overhaul** – Pytest suites rely on local fixtures, compatibility shims, and Celery workflow coverage. Graph-backed
   retrieval, Neo4j connectivity shims, and CLI admin helpers now have dedicated tests; continue adding cross-backend integration
   coverage.
2. **Automation & CI** – Makefile provides lint/format/type/test targets and CI runs fmt-check + pytest. Add caching and matrix
   builds when dependencies stabilize.
3. **Environment Provisioning** – Docker Compose now provisions Memgraph, Redis, and a Celery worker. Track multi-backend
   examples and ensure documentation stays current.

## Phase 5 – Strategic Enhancements (Planned)
1. **Graph-Backed Retrieval** – Push search workloads into the configured graph driver by leveraging backend-native vector/lexical indexes instead of loading namespace snapshots.
2. **Operational Observability** – Export telemetry to Prometheus/OpenTelemetry and surface dashboards/alerts.
3. **Celery Hardening** – Stress test consolidation/compression heuristics at scale and codify retry/backoff policies.
4. **Model Fidelity** – Replace compatibility shims with production-ready Pydantic models once dependency support catches up.
