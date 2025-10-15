# MeshMind Roadmap Task Breakdown

## 1. Ship official MCP server and tool suite
- **High-Level Task 1.1: Establish authenticated MCP server foundation**
  - **Subtask 1.1.a: Draft MCP authentication design doc** – Produce `docs/mcp/authentication.md` covering API key + OAuth2 handshake, token refresh policies, and error matrix, plus sequence diagram `docs/mcp/diagrams/auth_handshake.svg`; confirm via architecture sign-off comment and successful `make docs-lint` run.
  - **Subtask 1.1.b: Implement MCP server bootstrap package** – Scaffold `meshmind/mcp/server/__init__.py` with FastAPI app factory, dependency injection wiring, and configuration schema enforcing auth requirements; confirm by passing `uv run pytest tests/mcp/test_server_bootstrap.py`.
  - **Subtask 1.1.c: Add API key and OAuth2 verification middleware** – Implement `meshmind/mcp/server/auth.py` verifying API keys and JWTs, integrating with Redis cache for token revocation; confirm via unit tests `tests/mcp/test_auth_middleware.py` and manual request replay in `examples/mcp/authentication.http` succeeding with valid tokens and failing with revoked ones.
- **High-Level Task 1.2: Deliver memory management MCP endpoints**
  - **Subtask 1.2.a: Implement POST /mcp/memories endpoint** – Add FastAPI route handling JSON Schema `schemas/mcp/memory_create.json`, persist via `meshmind/storage/memory_repository.py`, and enqueue embedding jobs; confirm via integration test `tests/mcp/test_create_memory_endpoint.py` and contract test using `schemathesis`.
  - **Subtask 1.2.b: Implement GET /mcp/memories/{id} endpoint** – Provide retrieval with tenant scoping, hydration of related triplets, and 404 handling; confirm via `tests/mcp/test_get_memory_endpoint.py` and HTTP replay in `examples/mcp/query_memory.http`.
  - **Subtask 1.2.c: Implement DELETE /mcp/memories/{id} endpoint** – Ensure soft-delete with background purge, audit logging, and success semantics; verify via `tests/mcp/test_delete_memory_endpoint.py` and inspection of audit entries emitted to `docs/mcp/audit_samples.md`.
- **High-Level Task 1.3: Expose triplet and hygiene tooling**
  - **Subtask 1.3.a: Implement POST /mcp/triplets batch ingestion** – Support up to 100 triplets per request with validation and dedupe; confirm via `tests/mcp/test_create_triplets.py` and load test script `scripts/load/mcp_triplet_ingest.py` hitting SLA.
  - **Subtask 1.3.b: Implement POST /mcp/hygiene/rebuild endpoint** – Trigger graph maintenance job invoking `meshmind/graph/hygiene.py`; confirm via job execution log in `run/logs/hygiene_job.log` and unit tests `tests/graph/test_hygiene_runner.py`.
  - **Subtask 1.3.c: Publish MCP tool metadata** – Generate `docs/mcp/tools_catalog.json` enumerating endpoints, arguments, and success codes for IDE integrations; verify via JSON Schema validation `scripts/validate_tools_catalog.py` and review approval.

## 2. Introduce multi-level scoping and tenancy
- **High-Level Task 2.1: Extend domain models with tenancy identifiers**
  - **Subtask 2.1.a: Update persistence schemas for tenant scopes** – Add `tenant_id`, `agent_id`, `session_id`, and `run_id` columns to relational tables and vector collections via Alembic migration `alembic/versions/xxxx_add_scopes.py`; confirm by running `uv run alembic upgrade head` and schema snapshot tests.
  - **Subtask 2.1.b: Add scoped dataclasses and validators** – Modify `meshmind/domain/memory.py` and `triplet.py` to require scope identifiers with pydantic validation; confirm via `uv run pytest tests/domain/test_scope_validation.py`.
  - **Subtask 2.1.c: Update repositories for scope-aware queries** – Ensure all repository methods accept scope filters and enforce default tenant scoping; verify via `tests/storage/test_scope_filters.py`.
- **High-Level Task 2.2: Implement tenant-aware request context propagation**
  - **Subtask 2.2.a: Add request context middleware** – Create `meshmind/api/context.py` extracting scope IDs from headers and injecting into contextvars; verify via `tests/api/test_request_context.py`.
  - **Subtask 2.2.b: Wire scope context through services** – Update service layer functions to read contextvars and pass scope IDs to repositories; confirm by passing `tests/services/test_scope_context.py` and ensuring no scope-less calls via static analysis script `scripts/check_scope_context.py`.
  - **Subtask 2.2.c: Document scope header contracts** – Add `docs/api/tenancy_scopes.md` describing required headers, error codes, and sample client usage; verify via `make docs-lint` and reviewer approval.
- **High-Level Task 2.3: Provide tenant management tooling**
  - **Subtask 2.3.a: Build admin API for tenant lifecycle** – Implement POST/GET/DELETE `/admin/tenants` endpoints with RBAC guard; verify via `tests/admin/test_tenant_api.py`.
  - **Subtask 2.3.b: Add tenant-aware rate limiting** – Configure Redis-based rate limiter keyed by tenant and agent IDs; confirm via `tests/api/test_rate_limiting.py` and k6 script `scripts/load/test_rate_limit.js` showing throttle behavior.
  - **Subtask 2.3.c: Implement tenant reset CLI command** – Add `uv run meshmind-cli tenants reset --tenant-id <id>` clearing scoped data after confirmation; confirm via CLI integration test `tests/cli/test_tenant_reset.py`.

## 3. Adopt bi-temporal graph edges
- **High-Level Task 3.1: Extend graph schema for bi-temporality**
  - **Subtask 3.1.a: Update graph edge storage model** – Add `valid_from`, `valid_to`, `recorded_at`, and `superseded_by` fields in graph database schema; confirm via migration `alembic/versions/xxxx_bitemporal_edges.py` and schema snapshot tests.
  - **Subtask 3.1.b: Enhance edge ingestion pipeline** – Modify edge creation logic to accept temporal metadata and default windows; verify via `tests/graph/test_edge_ingestion_temporal.py`.
  - **Subtask 3.1.c: Provide temporal consistency constraints** – Implement data quality checks preventing overlapping valid windows; confirm via `tests/graph/test_temporal_constraints.py`.
- **High-Level Task 3.2: Support temporal queries**
  - **Subtask 3.2.a: Implement `as_of` query parameter** – Extend retrieval API to accept `as_of` timestamp and filter edges appropriately; verify via `tests/retrieval/test_as_of_queries.py`.
  - **Subtask 3.2.b: Add change-log queries** – Provide endpoint `/graph/edges/history` returning transaction timeline; confirm via `tests/graph/test_edge_history_endpoint.py` and docs snippet in `docs/api/examples/edge_history.md`.
  - **Subtask 3.2.c: Optimize temporal index performance** – Introduce database indexes on temporal fields and benchmark with `scripts/benchmarks/temporal_queries.py`; success criterion: p95 latency < 200ms for 10k edges.
- **High-Level Task 3.3: Automate temporal invalidation**
  - **Subtask 3.3.a: Build expiry scheduler** – Create cron job `meshmind/jobs/temporal_invalidation.py` closing edges when `valid_to` passed; confirm via `tests/jobs/test_temporal_invalidation.py`.
  - **Subtask 3.3.b: Emit invalidation audit events** – Publish events to `audit.temporal.edge.closed` topic with payload schema documented in `docs/events/temporal_edge_closed.json`; verify by replaying events in `tests/events/test_temporal_events.py`.
  - **Subtask 3.3.c: Provide admin dashboard widgets** – Add Grafana panel `dashboards/temporal_invalidation.json` showing counts of expired edges processed daily; confirm by screenshot artifact stored under `docs/observability/screenshots/temporal_dashboard.png`.

## 4. Expand hybrid retrieval and reranking
- **High-Level Task 4.1: Implement BM25 + embedding fusion**
  - **Subtask 4.1.a: Integrate BM25 scorer** – Add Whoosh/Lucene-based BM25 scoring module `meshmind/retrieval/bm25.py`; confirm via `tests/retrieval/test_bm25_scores.py`.
  - **Subtask 4.1.b: Build fusion service** – Implement Reciprocal Rank Fusion and MMR combination engine in `meshmind/retrieval/fusion.py` configurable via weights; verify via `tests/retrieval/test_fusion_strategies.py`.
  - **Subtask 4.1.c: Expose configuration API** – Provide `/retrieval/config` endpoints to update fusion weights per tenant; confirm via `tests/retrieval/test_config_api.py`.
- **High-Level Task 4.2: Add node-distance boosts and traversal recipes**
  - **Subtask 4.2.a: Compute graph distance heuristics** – Implement `meshmind/graph/distance.py` calculating BFS levels and caching results; verify via `tests/graph/test_distance_metrics.py`.
  - **Subtask 4.2.b: Incorporate distance boosts into reranker** – Update reranking pipeline to apply boosts for focal entity matches; confirm via `tests/retrieval/test_distance_boosts.py` comparing metrics vs baseline.
  - **Subtask 4.2.c: Document traversal recipes** – Publish `docs/retrieval/traversal_recipes.md` containing recommended BFS configurations and sample YAML; confirm via docs linting and retrieval workshop review sign-off.
- **High-Level Task 4.3: Benchmark hybrid retrieval**
  - **Subtask 4.3.a: Create evaluation datasets** – Produce dataset `data/eval/hybrid_retrieval.jsonl` with labeled queries; confirm via checksum tracked in `docs/eval/datasets.md`.
  - **Subtask 4.3.b: Automate metric reporting** – Extend evaluation harness to compute Recall@k, MRR, and NDCG for each recipe; verify via `uv run python scripts/eval/run_hybrid_metrics.py` generating `reports/hybrid_retrieval_report.md`.
  - **Subtask 4.3.c: Publish benchmark dashboard** – Add Grafana dashboard `dashboards/retrieval_performance.json` visualizing metrics per tenant; confirm via screenshot saved to `docs/observability/screenshots/retrieval_dashboard.png`.

## 5. Harden auth and governance
- **High-Level Task 5.1: Implement unified identity and access controls**
  - **Subtask 5.1.a: Add API key issuance API** – Create `/admin/api-keys` endpoints with hashed storage and TTL management; confirm via `tests/admin/test_api_keys.py`.
  - **Subtask 5.1.b: Integrate JWT verification with JWKS rotation** – Wire JWKS fetcher and caching in `meshmind/security/jwt.py`; verify via `tests/security/test_jwt_rotation.py` and live rotation drill script.
  - **Subtask 5.1.c: Configure role-based access control** – Define roles/permissions matrix in `config/rbac.yaml` and enforce via decorator; confirm via `tests/security/test_rbac_enforcement.py`.
- **High-Level Task 5.2: Enforce data governance policies**
  - **Subtask 5.2.a: Implement PII detection pipeline** – Integrate Presidio or custom detectors triggered on ingestion, logging redactions; verify via `tests/governance/test_pii_detection.py`.
  - **Subtask 5.2.b: Add retention policy scheduler** – Build job `meshmind/jobs/retention_policy.py` purging data after configured TTL; confirm via `tests/jobs/test_retention_policy.py` and manual dry-run log.
  - **Subtask 5.2.c: Encrypt sensitive storage at rest** – Enable envelope encryption for blob/vector stores, documenting KMS setup in `docs/security/encryption.md`; verify by encryption audit script `scripts/security/verify_encryption.py`.
- **High-Level Task 5.3: Provide governance observability**
  - **Subtask 5.3.a: Emit moderation audit logs** – Configure structured logging to `audit.moderation` sink with retention; confirm via `tests/audit/test_moderation_logs.py`.
  - **Subtask 5.3.b: Build governance dashboard** – Create Grafana panels monitoring PII detections, redactions, retention actions; confirm via screenshot `docs/observability/screenshots/governance_dashboard.png`.
  - **Subtask 5.3.c: Publish compliance playbook** – Author `docs/security/compliance_playbook.md` mapping controls to SOC2/GDPR requirements; verify via security review sign-off.

## 6. Deliver consolidation planner and maintenance intelligence
- **High-Level Task 6.1: Build LLM-assisted consolidation planner**
  - **Subtask 6.1.a: Define planner prompt templates** – Store prompts in `meshmind/planner/prompts.yaml` covering ADD/UPDATE/DELETE flows; confirm via `tests/planner/test_prompt_loading.py`.
  - **Subtask 6.1.b: Implement planner orchestration service** – Add `meshmind/planner/service.py` invoking LLM, evaluating conflicts, and emitting plan steps; verify via `tests/planner/test_service_outputs.py` with mocked LLM.
  - **Subtask 6.1.c: Integrate planner with MCP endpoints** – Wire planner output to `POST /mcp/hygiene/plan` returning actionable steps; confirm via integration test `tests/mcp/test_hygiene_plan_endpoint.py`.
- **High-Level Task 6.2: Detect contradictions and duplicates**
  - **Subtask 6.2.a: Implement contradiction detection heuristics** – Add rule engine `meshmind/planner/contradiction_rules.py` comparing memory facts; verify via `tests/planner/test_contradiction_rules.py`.
  - **Subtask 6.2.b: Build similarity dedupe job** – Create periodic job `meshmind/jobs/dedupe_similar_memories.py` leveraging embeddings; confirm via `tests/jobs/test_dedupe_job.py`.
  - **Subtask 6.2.c: Surface maintenance alerts** – Add notifications to Slack/webhook via `meshmind/alerts/maintenance.py`; verify via `tests/alerts/test_maintenance_notifications.py`.
- **High-Level Task 6.3: Provide replayable change logs and reset tooling**
  - **Subtask 6.3.a: Persist change events** – Store planner-executed changes in `change_logs` table with diff payloads; confirm via migration and `tests/storage/test_change_logs.py`.
  - **Subtask 6.3.b: Build replay CLI** – Implement `meshmind-cli changelog replay --plan-id` applying stored diffs; verify via CLI test `tests/cli/test_changelog_replay.py`.
  - **Subtask 6.3.c: Implement scope-level reset endpoint** – Provide `/admin/scopes/reset` removing data for session/run; confirm via `tests/admin/test_scope_reset.py`.

## 7. Stand up full OpenTelemetry observability
- **High-Level Task 7.1: Instrument services with tracing**
  - **Subtask 7.1.a: Configure OTLP exporter** – Add `meshmind/observability/tracing.py` wiring OTLP exporter to collector; verify via `tests/observability/test_tracing_config.py` and manual Jaeger trace check.
  - **Subtask 7.1.b: Add span decorators** – Instrument API routes, storage, and LLM calls with spans capturing attributes; confirm via `tests/observability/test_span_attributes.py`.
  - **Subtask 7.1.c: Document tracing setup** – Write `docs/observability/tracing.md` including deployment instructions; verify via docs lint.
- **High-Level Task 7.2: Publish metrics and dashboards**
  - **Subtask 7.2.a: Emit ingestion/retrieval metrics** – Expose Prometheus metrics via `/metrics` endpoint; confirm via `tests/observability/test_metrics_endpoint.py`.
  - **Subtask 7.2.b: Build Grafana dashboards** – Create dashboards for latency, recall, error rate saved under `dashboards/core_service.json`; confirm via screenshot `docs/observability/screenshots/core_dashboard.png`.
  - **Subtask 7.2.c: Automate SLO alerts** – Configure Alertmanager rules `observability/alerts/slo_rules.yaml`; verify via alert firing in staging drill recorded in `docs/observability/drills/slo_alert.md`.
- **High-Level Task 7.3: Integrate logs with traces**
  - **Subtask 7.3.a: Enable structured logging** – Update logging config to output trace/span IDs; confirm via `tests/observability/test_structured_logs.py`.
  - **Subtask 7.3.b: Configure log shipping** – Deploy OpenTelemetry collector pipeline sending logs to ELK; verify via infrastructure test plan `docs/observability/log_shipping_validation.md`.
  - **Subtask 7.3.c: Provide observability runbooks** – Author `docs/observability/runbooks/ingestion_latency.md` with remediation steps; confirm via on-call review acknowledgment.

## 8. Broaden provider and backend flexibility
- **High-Level Task 8.1: Add Qdrant backend support**
  - **Subtask 8.1.a: Implement Qdrant client adapter** – Create `meshmind/storage/vector/qdrant_adapter.py` supporting CRUD operations; verify via `tests/storage/vector/test_qdrant_adapter.py`.
  - **Subtask 8.1.b: Provide migration scripts** – Add CLI command `meshmind-cli backend migrate-to-qdrant`; confirm via integration test `tests/cli/test_backend_migration_qdrant.py`.
  - **Subtask 8.1.c: Document Qdrant deployment guide** – Publish `docs/backends/qdrant.md` covering setup, scaling, and trade-offs; confirm via docs lint.
- **High-Level Task 8.2: Integrate Chroma backend**
  - **Subtask 8.2.a: Build Chroma adapter** – Implement `meshmind/storage/vector/chroma_adapter.py`; verify via `tests/storage/vector/test_chroma_adapter.py`.
  - **Subtask 8.2.b: Support hybrid backend selection** – Extend config to allow per-tenant backend choice stored in `config/backends.yaml`; confirm via `tests/config/test_backend_selection.py`.
  - **Subtask 8.2.c: Provide benchmarking scripts** – Add `scripts/benchmarks/chroma_vs_qdrant.py`; confirm via generated report `reports/backends/chroma_vs_qdrant.md`.
- **High-Level Task 8.3: Add Azure AI Search integration**
  - **Subtask 8.3.a: Implement Azure Search adapter** – Create `meshmind/storage/vector/azure_search_adapter.py` with retry logic; verify via `tests/storage/vector/test_azure_adapter.py`.
  - **Subtask 8.3.b: Add latency/cost analytics** – Capture per-backend latency and cost metrics emitted to Prometheus; confirm via `tests/observability/test_backend_metrics.py` and dashboard updates.
  - **Subtask 8.3.c: Publish backend selection guide** – Write `docs/backends/selection_guide.md` comparing Qdrant, Chroma, Azure Search with decision tree; verify via product review approval.

## 9. Launch SDKs and ecosystem starter kits
- **High-Level Task 9.1: Ship Python SDK**
  - **Subtask 9.1.a: Scaffold Python SDK package** – Create `sdk/python/meshmind/__init__.py` with client, auth, and error modules; confirm via `uv run pytest sdk/python/tests`.
  - **Subtask 9.1.b: Implement high-level client methods** – Add memory, triplet, retrieval, and admin wrappers with retries; verify via integration tests hitting local MCP server.
  - **Subtask 9.1.c: Publish Python SDK docs** – Generate `docs/sdk/python/index.md` with quickstart and API reference; confirm via `make docs-build`.
- **High-Level Task 9.2: Ship TypeScript SDK**
  - **Subtask 9.2.a: Initialize TypeScript package** – Set up `sdk/typescript/package.json` with build/test pipeline; confirm via `pnpm test`.
  - **Subtask 9.2.b: Implement MCP client modules** – Provide typed clients for memory/triplet endpoints with Zod validation; verify via `pnpm test` and `pnpm lint`.
  - **Subtask 9.2.c: Publish typed docs** – Generate API reference using TypeDoc output stored in `docs/sdk/typescript`; confirm via CI artifact.
- **High-Level Task 9.3: Deliver ecosystem templates and CLI enhancements**
  - **Subtask 9.3.a: Create LangGraph starter** – Add `examples/langgraph/starter.ipynb` demonstrating retrieval workflow; confirm via CI `nbval` test.
  - **Subtask 9.3.b: Build CrewAI template** – Add `examples/crewai/project_template/README.md` and scripts; verify via manual run instructions executed in CI job.
  - **Subtask 9.3.c: Enhance CLI admin commands** – Implement commands for reindex, compact, prune, export, import in `meshmind-cli`; confirm via `tests/cli/test_admin_commands.py`.

## 10. Publish evaluation harness and benchmarks
- **High-Level Task 10.1: Assemble evaluation datasets**
  - **Subtask 10.1.a: Curate synthetic benchmark data** – Generate dataset `data/eval/synthetic_memories.jsonl` with ground truth labels; confirm via data review and checksum log.
  - **Subtask 10.1.b: Import public datasets** – Integrate open QA dataset pipeline into `scripts/eval/import_public_datasets.py`; verify via dataset availability in `data/eval/public/`.
  - **Subtask 10.1.c: Document dataset provenance** – Write `docs/eval/dataset_provenance.md` listing sources, licenses, and usage constraints; confirm via docs lint.
- **High-Level Task 10.2: Build scoring harness**
  - **Subtask 10.2.a: Implement evaluation runner** – Create `meshmind/eval/runner.py` executing retrieval with metrics; verify via `uv run pytest tests/eval/test_runner.py`.
  - **Subtask 10.2.b: Add metric computations** – Implement Recall@k, MRR, NDCG, latency, token cost calculators in `meshmind/eval/metrics.py`; confirm via unit tests `tests/eval/test_metrics.py`.
  - **Subtask 10.2.c: Automate regression dashboards** – Publish `reports/eval/regression_dashboard.md` generated by CI job; confirm via pipeline artifact link.
- **High-Level Task 10.3: Integrate harness into CI/CD**
  - **Subtask 10.3.a: Add nightly evaluation workflow** – Create GitHub Action `.github/workflows/nightly_eval.yml` running harness; confirm via first successful run badge.
  - **Subtask 10.3.b: Gate releases on evaluation thresholds** – Update release pipeline to enforce metric floors stored in `config/eval_thresholds.yaml`; verify via simulated failure.
  - **Subtask 10.3.c: Publish evaluation API** – Provide `/eval/runs` endpoints to trigger evaluations and fetch results; confirm via `tests/eval/test_eval_api.py`.

## 11. Enable graph-aware personalization
- **High-Level Task 11.1: Model persona graphs**
  - **Subtask 11.1.a: Design persona schema** – Define persona nodes/edges in `docs/personalization/persona_schema.md` and update migrations accordingly; verify via schema tests.
  - **Subtask 11.1.b: Implement persona ingestion API** – Add `/persona` endpoints for CRUD operations with validation; confirm via `tests/personalization/test_persona_api.py`.
  - **Subtask 11.1.c: Capture implicit feedback** – Instrument client SDKs to send interaction signals to `/persona/events`; verify via telemetry logs and `tests/personalization/test_feedback_capture.py`.
- **High-Level Task 11.2: Apply personalization in retrieval**
  - **Subtask 11.2.a: Compute preference embeddings** – Implement module `meshmind/personalization/embeddings.py` generating preference vectors; verify via `tests/personalization/test_preference_embeddings.py`.
  - **Subtask 11.2.b: Adjust reranker with persona context** – Modify reranker to blend persona scores; confirm via A/B test script `scripts/personalization/ab_test.py` meeting uplift target.
  - **Subtask 11.2.c: Add adaptive rerank configuration UI** – Extend admin UI `docs/ui/personalization_config.md` screenshot to show controls; confirm via manual QA checklist.
- **High-Level Task 11.3: Learn from stored preferences**
  - **Subtask 11.3.a: Implement feedback loop jobs** – Create job `meshmind/jobs/update_persona_preferences.py` recalculating weights nightly; verify via `tests/jobs/test_persona_update_job.py`.
  - **Subtask 11.3.b: Provide personalization analytics** – Add dashboard `dashboards/personalization.json`; confirm via screenshot `docs/observability/screenshots/personalization_dashboard.png`.
  - **Subtask 11.3.c: Document privacy controls** – Write `docs/personalization/privacy_controls.md` outlining opt-out flows and data erasure; verify via legal review sign-off.

## 12. Provide browser and MCP ingestion workflows
- **High-Level Task 12.1: Build browser extension**
  - **Subtask 12.1.a: Scaffold Chrome extension** – Create `clients/browser/chrome/manifest.json` with OAuth flow; confirm via Chrome web store lint tool report.
  - **Subtask 12.1.b: Implement content capture UI** – Develop React-based popup in `clients/browser/chrome/src` capturing highlights and annotations; verify via Jest + Playwright tests.
  - **Subtask 12.1.c: Add provenance metadata transmission** – Ensure extension posts to MCP with URL, timestamp, author metadata; confirm via integration test hitting local server.
- **High-Level Task 12.2: Provide MCP CLI ingestion**
  - **Subtask 12.2.a: Extend CLI for bulk uploads** – Implement `meshmind-cli mcp ingest --file` command parsing Markdown/HTML; verify via CLI tests.
  - **Subtask 12.2.b: Support annotation defaults** – Add configuration file `~/.meshmind/ingest_defaults.yaml` applied to CLI and extension; confirm via `tests/cli/test_ingest_defaults.py`.
  - **Subtask 12.2.c: Document ingestion workflows** – Publish `docs/ingestion/browser_cli_workflows.md` with screenshots and troubleshooting; confirm via docs lint.
- **High-Level Task 12.3: Implement webhook ingestion**
  - **Subtask 12.3.a: Build `/ingest/webhook` endpoint** – Accept signed payloads, validate provenance, and queue ingestion; verify via `tests/ingestion/test_webhook_endpoint.py`.
  - **Subtask 12.3.b: Configure signature verification** – Support HMAC and public-key signatures stored per tenant; confirm via `tests/ingestion/test_signature_verification.py`.
  - **Subtask 12.3.c: Provide webhook onboarding kit** – Deliver sample Postman collection `examples/ingestion/webhook.postman_collection.json`; confirm via QA review.

## 13. Offer hosted MeshMind tiers
- **High-Level Task 13.1: Architect multi-tenant hosting platform**
  - **Subtask 13.1.a: Define infrastructure blueprint** – Document Terraform modules in `infrastructure/blueprints/hosted_tiers.md` detailing networking, scaling, and isolation; confirm via architecture review.
  - **Subtask 13.1.b: Implement tenant provisioning automation** – Create Terraform + Ansible scripts invoked by `scripts/infra/provision_tenant.py`; verify via staging tenant creation log.
  - **Subtask 13.1.c: Configure billing metrics pipeline** – Emit usage metrics to billing topic `billing.usage.metrics`; confirm via `tests/billing/test_usage_metrics.py`.
- **High-Level Task 13.2: Add SSO and quota management**
  - **Subtask 13.2.a: Integrate SSO providers** – Support SAML and OIDC connectors configured per tenant; verify via `tests/security/test_sso_integration.py`.
  - **Subtask 13.2.b: Implement quota enforcement** – Track API usage vs plan quotas and return 429 with plan upgrade link; confirm via `tests/billing/test_quota_enforcement.py`.
  - **Subtask 13.2.c: Build billing admin UI** – Provide dashboard `clients/admin/hosted_billing` showing usage and invoices; verify via Cypress tests.
- **High-Level Task 13.3: Support migration tooling**
  - **Subtask 13.3.a: Develop self-hosted export kit** – Create `scripts/migration/export_self_hosted.py` packaging data; confirm via integration test migrating fixture data.
  - **Subtask 13.3.b: Implement hosted import pipeline** – Provide `/admin/migrations/import` endpoint consuming export bundles; verify via `tests/admin/test_migration_import.py`.
  - **Subtask 13.3.c: Document migration runbook** – Write `docs/hosted/migration_runbook.md` with step-by-step instructions; confirm via support team approval.

## 14. Roll out data governance and compliance tooling
- **High-Level Task 14.1: Deploy PII detection and redaction**
  - **Subtask 14.1.a: Integrate PII detection ruleset** – Extend ingestion pipeline with regex + ML detectors configured in `config/pii_rules.yaml`; verify via `tests/governance/test_pii_ruleset.py`.
  - **Subtask 14.1.b: Implement redaction workflows** – Replace detected PII with placeholders, storing original encrypted references; confirm via `tests/governance/test_redaction_workflow.py`.
  - **Subtask 14.1.c: Surface PII audit reports** – Generate weekly report `reports/governance/pii_audit.csv`; confirm via scheduled job output.
- **High-Level Task 14.2: Manage retention and legal holds**
  - **Subtask 14.2.a: Add legal hold flagging** – Allow setting holds per tenant/memory preventing deletion; verify via `tests/governance/test_legal_holds.py`.
  - **Subtask 14.2.b: Provide retention configuration UI** – Build admin panel `clients/admin/governance/retention` for TTL settings; confirm via Cypress tests.
  - **Subtask 14.2.c: Document retention policy procedures** – Author `docs/governance/retention_policies.md` referencing compliance obligations; verify via legal approval.
- **High-Level Task 14.3: Deliver compliance dashboards**
  - **Subtask 14.3.a: Implement compliance metrics exporter** – Emit metrics for deletions, holds, redactions to Prometheus; confirm via `tests/governance/test_compliance_metrics.py`.
  - **Subtask 14.3.b: Build compliance reporting UI** – Add dashboards `dashboards/compliance.json`; verify via screenshot stored in docs.
  - **Subtask 14.3.c: Provide audit trail exports** – Implement `/admin/audit/export` generating signed CSV; confirm via `tests/admin/test_audit_export.py`.

## 15. Activate advanced safety and resilience
- **High-Level Task 15.1: Monitor abuse and anomalies**
  - **Subtask 15.1.a: Add anomaly detection pipeline** – Use statistical models on request metrics stored in `meshmind/safety/anomaly_detector.py`; verify via `tests/safety/test_anomaly_detector.py`.
  - **Subtask 15.1.b: Implement abuse classifier** – Train LLM-based classifier for malicious inputs stored in `models/abuse_classifier`; confirm via evaluation report `reports/safety/abuse_classifier.md`.
  - **Subtask 15.1.c: Route incidents to on-call** – Integrate with PagerDuty via `meshmind/alerts/pagerduty.py`; verify via sandbox incident trigger.
- **High-Level Task 15.2: Automate backups and restores**
  - **Subtask 15.2.a: Schedule automated backups** – Configure snapshots for databases/vector stores with scripts `scripts/backups/run_backup.py`; confirm via backup log retention.
  - **Subtask 15.2.b: Implement time-travel restore CLI** – Build `meshmind-cli resilience restore --timestamp` orchestrating rollback; verify via integration test `tests/cli/test_restore_command.py`.
  - **Subtask 15.2.c: Document disaster recovery plan** – Write `docs/resilience/disaster_recovery.md` including RPO/RTO targets; confirm via leadership sign-off.
- **High-Level Task 15.3: Conduct chaos testing**
  - **Subtask 15.3.a: Implement chaos scenarios** – Use Chaos Mesh or custom scripts in `scripts/chaos/` injecting faults; confirm via run log `reports/resilience/chaos_run_1.md`.
  - **Subtask 15.3.b: Measure resilience metrics** – Capture recovery time metrics exported to Grafana; confirm via dashboard screenshot `docs/observability/screenshots/resilience_dashboard.png`.
  - **Subtask 15.3.c: Iterate on remediation playbooks** – Update `docs/resilience/chaos_playbooks.md` after each test; verify via postmortem review note.

## 16. Sustain ongoing competitive analysis
- **High-Level Task 16.1: Formalize research cadence**
  - **Subtask 16.1.a: Schedule quarterly review meetings** – Add calendar automation script `scripts/research/schedule_reviews.py` emailing stakeholders; confirm via calendar invites snapshot.
  - **Subtask 16.1.b: Maintain competitor matrix** – Update `docs/research/competitor_matrix.xlsx` quarterly with feature parity notes; verify via change log entry.
  - **Subtask 16.1.c: Publish insights digest** – Issue quarterly memo `docs/research/digests/QxYYYY.md` summarizing findings; confirm via leadership acknowledgement.
- **High-Level Task 16.2: Track roadmap adjustments**
  - **Subtask 16.2.a: Update roadmap alignment process** – Document `docs/research/roadmap_review_process.md` describing scoring rubric; confirm via product council approval.
  - **Subtask 16.2.b: Automate feature gap alerts** – Build script `scripts/research/gap_alerts.py` comparing competitor features vs backlog; verify via alert email in staging.
  - **Subtask 16.2.c: Maintain research repository** – Organize sources in `research/README.md` with tagging; confirm via repo review.
- **High-Level Task 16.3: Foster community intelligence**
  - **Subtask 16.3.a: Launch feedback intake form** – Create form integrated with MeshMind backend storing insights in `community_feedback` table; verify via test submissions.
  - **Subtask 16.3.b: Monitor industry announcements** – Configure RSS/LLM watcher `scripts/research/monitor_announcements.py`; confirm via weekly digest log `reports/research/announcement_digest.md`.
  - **Subtask 16.3.c: Host partner roundtables** – Plan quarterly roundtables documented in `docs/research/partner_roundtables.md` including agendas and outcomes; confirm via attendee feedback survey snapshot.
