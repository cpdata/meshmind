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
   Graph-backed wrappers now rely on driver-side filtering, pagination, and aggregation before in-memory scoring. Next: push
   similarity computation into Memgraph/Neo4j so vector rankings can execute server-side without Python hydration.
2. **Maintenance Tasks** – Tasks emit telemetry and persist consolidation/compression results. Consolidation planning enforces
   batch/backoff thresholds and surfaces skipped groups. Next: validate heuristics on larger datasets and tune the thresholds with
   real data.
3. **Importance Scoring Improvements** – Heuristic scoring is live and now records distribution metrics via telemetry. Next:
   design data-driven evaluation loops or LLM-assisted ranking to tune weights over time.
4. **LLM Provider Flexibility** – Direct `openai` usage has been consolidated behind `meshmind.llm_client`. The wrapper
   honors `LLM_*` environment variables, CLI flags, and REST/gRPC payload overrides (`use_llm_rerank`, `llm_models`,
   `llm_base_urls`, `llm_api_key`, `rerank_model`). Timestamp utilities have been standardized on timezone-aware UTC defaults.
   Next: validate live provider integrations once external credentials and network routing are provisioned.

## Phase 4 – Developer Experience & Tooling (In Progress)
1. **Testing Overhaul** – Pytest suites rely on local fixtures, compatibility shims, and Celery workflow coverage. Graph-backed
   retrieval, Neo4j connectivity shims, CLI admin helpers, and the documentation guard script now have dedicated tests; continue
   adding cross-backend integration coverage and mirror shim retirement progress in `DUMMIES.md` so integration suites can
   replace them incrementally.
2. **Automation & CI** – Makefile provides lint/format/type/test/docs-guard targets and CI runs fmt-check, docs guard, and
   pytest. Add caching and matrix builds when dependencies stabilize.
3. **Environment Provisioning** – Docker Compose now provisions Memgraph, Neo4j, and Redis (with targeted stacks for tests).
   Track multi-backend examples, document the new `SETUP.md`, keep docs current, and distribute the new `run/install_setup.sh`
   and `run/maintenance_setup.sh` automation scripts for environment bootstrap.

## Phase 5 – Strategic Enhancements (Planned)
1. **Graph-Backed Retrieval** – Extend the new driver-side filtering/pagination to full vector/lexical execution using backend-native indexes to avoid round-tripping candidate embeddings.
2. **Operational Observability** – Export telemetry to Prometheus/OpenTelemetry and surface dashboards/alerts.
3. **Celery Hardening** – Stress test consolidation/compression heuristics at scale and codify retry/backoff policies.
4. **Model Fidelity** – Replace compatibility shims with production-ready Pydantic models once dependency support catches up.
