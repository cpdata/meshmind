# Recommendations

## Stabilize the Foundation
- Maintain lazy initialization for optional dependencies and continue testing environments without Memgraph or OpenAI access.
- Align declared Python support with dependency compatibility (target 3.11/3.12 until third parties certify 3.13).
- Harden the OpenAI embedding adapter to consume SDK response objects directly and surface actionable errors for rate limits.
- Add automated smoke tests for the new SQLite/Neo4j drivers to ensure regressions are caught early.

## Restore and Extend Functionality
- Implement graph-backed retrieval queries so callers are not required to materialize memory lists in Python.
- Persist consolidation outputs back into the graph and close the loop on maintenance workflows.
- Design richer importance scoring heuristics (analytics-driven or LLM-evaluated) to replace the current constant fallback.
- Expand predicate/registry management APIs so custom relationship vocabularies can be registered explicitly.

## Improve Developer Experience
- Document usage patterns for each graph backend (memory/sqlite/memgraph/neo4j) and provide Makefile shortcuts for switching.
- Add Makefile targets for running Celery workers and seeding demo data once infrastructure is provisioned.
- Broaden pytest coverage to include Celery tasks, graph-backed retrieval, and error handling scenarios.
- Cache dependencies and split lint/test jobs in CI for faster feedback once the dependency stack stabilizes.

## Documentation & Onboarding
- Keep `README_LATEST.md`, `SOT.md`, and onboarding guides synchronized with each release; document rerank, retrieval, and
  registry flows with diagrams when possible.
- Publish troubleshooting sections for missing optional tooling (ruff, pyright, typeguard, toml-sort, yamllint) now referenced in
  the Makefile.
- Provide walkthroughs for configuring LLM reranking, including sample prompts and response expectations.
- Add onboarding notes for the REST/gRPC service layers with sample payloads and curl/grpcurl snippets.

## Future Enhancements
- Export telemetry to Prometheus/OpenTelemetry and wire alerts/dashboards around ingestion and maintenance.
- Explore streaming ingestion pipelines (queues, webhooks) for near-real-time updates.
- Investigate lightweight web UI tooling for inspecting memories, triplets, and telemetry snapshots.
