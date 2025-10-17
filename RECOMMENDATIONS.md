# Recommendations

## Stabilize the Foundation
- Maintain lazy initialization for optional dependencies and continue testing environments without Memgraph or LLM provider access.
- Maintain declared Python support at `>=3.11,<3.13` and monitor dependency releases before widening the range.
- Harden the LLM-backed embedding adapter to consume SDK response objects directly and surface actionable errors for rate limits.
- Expand automated smoke coverage (counts endpoints, maintenance retries) to the new SQLite/Neo4j drivers to ensure regressions are caught early.
- Continue using `DUMMIES.md` to track remaining shims (gRPC stub, fake drivers) and log retirements as dependencies graduate into the default bootstrap path.

## Restore and Extend Functionality
- Extend the new server-side filtering and pagination work by pushing similarity ranking into Memgraph/Neo4j so vector scoring runs without loading namespaces in Python.
- Validate consolidation heuristics at scale and tune the new exponential backoff settings (`MAINTENANCE_MAX_ATTEMPTS`, `MAINTENANCE_BASE_DELAY_SECONDS`) before enabling automated writes in production.
- Leverage the new benchmarking scripts (`scripts/evaluate_importance.py`, `scripts/consolidation_benchmark.py`, `scripts/benchmark_pagination.py`) to validate heuristics and driver performance; schedule follow-up runs against production-sized datasets.
- Incorporate the live integration suite (`pytest -m integration`) into pre-release checklists so Memgraph/Neo4j/Redis workflows stay verified.
- Introduce feedback loops for the importance heuristic (e.g., LLM-assisted ranking or analytics-driven weights) to tune thresholds over time once real-world telemetry is available.
- Build on the new `meshmind.api.grpc_server` helpers and CLI entry point by
  publishing generated clients (Python + other languages) and exercising
  end-to-end smoke tests once infrastructure is available.
- Exercise the new `llm_client` overrides via REST/gRPC integration smoke tests (once credentials are available) to confirm per-request models/endpoints behave consistently outside unit tests.
- Expand predicate/registry management APIs beyond the CLI helper so services can manage vocabularies programmatically.
- Adhere to the Pydantic 2.x policy documented in `docs/development.md` (maintain Python 3.11–3.12 support, refresh locks when upstream ships 3.13 wheels, document migration notes alongside model changes).

## Improve Developer Experience
- Document usage patterns for each graph backend (memory/sqlite/memgraph/neo4j) inside `docs/` and keep the docs-guard mapping current so contributors know which pages to update when modules change.
- Add Makefile targets for running Celery workers and seeding demo data once infrastructure is provisioned (potentially reusing
  the new Docker Compose stacks).
- Broaden pytest coverage with cross-backend integration tests (Memgraph/Neo4j) and failure injection to complement the new graph retrieval, CLI admin, counts smoke, benchmark, and maintenance backoff tests.
- Cache dependencies and split lint/test jobs in CI for faster feedback once the dependency stack stabilizes.
- Maintain the new `run/install_setup.sh` and `run/maintenance_setup.sh` automation scripts alongside provisioning docs so environment bootstrap stays reproducible, and document timezone-aware timestamp expectations when integrating with downstream stores.

## Documentation & Onboarding
- Keep `README.md`, `SOT.md`, `docs/`, and onboarding guides synchronized with each release; document rerank, retrieval, and
  registry flows with diagrams when possible. The new synthetic dataset ingestion workflow in `docs/retrieval.md` should be
  incorporated into future onboarding materials.
- Maintain the troubleshooting section for optional tooling (ruff, pyright, typeguard, toml-sort, yamllint) now referenced in
  the Makefile and expand it as new developer utilities are introduced. Keep `SETUP.md` synchronized when dependencies change.
- Provide walkthroughs for configuring LLM reranking, including sample prompts and response expectations.
- Add onboarding notes for the REST/gRPC service layers with sample payloads and curl/grpcurl snippets.

## Future Enhancements
- Export telemetry to Prometheus/OpenTelemetry and wire alerts/dashboards around ingestion and maintenance.
- Explore streaming ingestion pipelines (queues, webhooks) for near-real-time updates.
- Investigate lightweight web UI tooling for inspecting memories, triplets, and telemetry snapshots.
