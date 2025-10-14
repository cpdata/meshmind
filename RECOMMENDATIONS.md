# Recommendations

## Stabilize the Foundation
- Maintain lazy initialization for optional dependencies and continue testing environments without Memgraph or OpenAI access.
- Maintain declared Python support at `>=3.11,<3.13` and monitor dependency releases before widening the range.
- Harden the OpenAI embedding adapter to consume SDK response objects directly and surface actionable errors for rate limits.
- Add automated smoke tests for the new SQLite/Neo4j drivers to ensure regressions are caught early.

## Restore and Extend Functionality
- Push graph-backed retrieval deeper into Memgraph/Neo4j so similarity ranking runs server-side instead of loading namespaces in Python.
- Validate consolidation heuristics at scale and tune the new batch/backoff thresholds before enabling automated writes in production.
- Introduce evaluation loops for the new importance heuristic (e.g., LLM-assisted ranking or analytics-driven weights) to tune thresholds over time, leveraging the telemetry stats now emitted.
- Expand predicate/registry management APIs beyond the CLI helper so services can manage vocabularies programmatically.
- Plan for reintroducing full Pydantic models once packaging support is aligned with target Python versions.

## Improve Developer Experience
- Document usage patterns for each graph backend (memory/sqlite/memgraph/neo4j) inside `docs/` and provide Makefile shortcuts for switching.
- Add Makefile targets for running Celery workers and seeding demo data once infrastructure is provisioned.
- Broaden pytest coverage with cross-backend integration tests (Memgraph/Neo4j) and failure injection to complement the new graph retrieval and CLI admin unit tests.
- Cache dependencies and split lint/test jobs in CI for faster feedback once the dependency stack stabilizes.

## Documentation & Onboarding
- Keep `README.md`, `SOT.md`, `docs/`, and onboarding guides synchronized with each release; document rerank, retrieval, and
  registry flows with diagrams when possible.
- Publish troubleshooting sections for missing optional tooling (ruff, pyright, typeguard, toml-sort, yamllint) now referenced in
  the Makefile.
- Provide walkthroughs for configuring LLM reranking, including sample prompts and response expectations.
- Add onboarding notes for the REST/gRPC service layers with sample payloads and curl/grpcurl snippets.

## Future Enhancements
- Export telemetry to Prometheus/OpenTelemetry and wire alerts/dashboards around ingestion and maintenance.
- Explore streaming ingestion pipelines (queues, webhooks) for near-real-time updates.
- Investigate lightweight web UI tooling for inspecting memories, triplets, and telemetry snapshots.
