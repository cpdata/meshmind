# Issues Checklist

> [!NOTE]
> Issue and task tracking lives in the Beads tracker (`bd`). Use this page as a quick orientation for the highest-impact items and check `bd show <issue>` for full details.

## Blockers
- [ ] `meshmind-95` – Provision a Celery worker + Redis staging stack so maintenance and integration tests can hit real services.
- [ ] `meshmind-96` – Deploy an authenticated REST/gRPC staging environment to validate curl/grpcurl documentation.
- [ ] `meshmind-98` – Stand up long-lived Memgraph/Neo4j clusters dedicated to benchmarking.
- [ ] `meshmind-99` – Regenerate and publish a ≥10k-memory synthetic dataset for consolidation benchmarks.
- [ ] `meshmind-101` – Restore outbound PyPI (or provide a mirror) so dependency locks can be regenerated.

## High Priority (next once blockers clear)
- [ ] `meshmind-82` – Implement backend-native vector similarity queries for Memgraph/Neo4j.
- [ ] `meshmind-83` – Run `scripts/consolidation_benchmark.py` with the refreshed dataset and document retry defaults.
- [ ] `meshmind-84` – Execute pagination benchmarks against the staging clusters and update retrieval guidance.
- [ ] `meshmind-85` – Add Celery/Redis-backed integration tests for maintenance retry flags.
- [ ] `meshmind-86` – Re-run curl/grpcurl documentation steps against the deployed staging endpoints.
- [ ] `meshmind-87` – Expand gRPC ingestion/search integration coverage once infrastructure lands.
- [ ] `meshmind-88` – Publish protobuf client artifacts after the release pipeline exists.
- [ ] `meshmind-89` – Automate the live integration suite in CI once maintenance tests pass.
- [ ] `meshmind-90` – Document ingestion workflows for the synthetic dataset generator after benchmarking.
- [ ] `meshmind-91` – Capture release notes for retiring REST/Celery shims once migration source material is ready.
- [ ] `meshmind-92` – Write gRPC CLI usage examples after the smoke tests complete.
- [ ] `meshmind-93` – Identify observability exporters and outline integration steps.
- [ ] `meshmind-94` – Explore UI concepts after the API hardening backlog (`meshmind-103`) lands.
- [ ] `meshmind-97` – Stand up the protobuf artifact release pipeline.
- [ ] `meshmind-100` – Gather authoritative REST/Celery retirement context for documentation.
- [ ] `meshmind-102` – Track upstream Pydantic packaging so the compatibility shim can be retired for good.
- [ ] `meshmind-103` – Finish the API hardening backlog to unblock downstream UX work.

## Reference
- Historical items completed prior to the Beads migration remain closed in the tracker (`bd list --status closed`).
- Use `bd ready` for the actionable queue after the blockers above are addressed.
