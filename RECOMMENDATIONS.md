# Recommendations

## Stabilize the Foundation
- Maintain lazy initialization for optional dependencies and continue testing environments without Memgraph or OpenAI access.
- Align declared Python support with dependency compatibility (target 3.11/3.12 until third parties certify 3.13).
- Harden the OpenAI embedding adapter to consume SDK response objects directly and surface actionable errors for rate limits.

## Restore and Extend Functionality
- Implement graph-backed retrieval queries so callers are not required to materialize memory lists in Python.
- Persist consolidation outputs back into the graph and close the loop on maintenance workflows.
- Design richer importance scoring heuristics (analytics-driven or LLM-evaluated) to replace the current constant fallback.
- Expand predicate/registry management APIs so custom relationship vocabularies can be registered explicitly.

## Improve Developer Experience
- Provision docker-compose services (or scripts) for Memgraph and Redis to streamline local setup.
- Add Makefile targets for running Celery workers and seeding demo data once infrastructure is provisioned.
- Broaden pytest coverage to include Celery tasks, graph-backed retrieval, and error handling scenarios.
- Cache dependencies and split lint/test jobs in CI for faster feedback once the dependency stack stabilizes.

## Documentation & Onboarding
- Keep `README_LATEST.md`, `SOT.md`, and onboarding guides synchronized with each release; document rerank, retrieval, and
  registry flows with diagrams when possible.
- Publish troubleshooting sections for missing optional tooling (ruff, pyright, typeguard, toml-sort, yamllint) now referenced in
  the Makefile.
- Provide walkthroughs for configuring LLM reranking, including sample prompts and response expectations.

## Future Enhancements
- Introduce alternative storage drivers (Neo4j, in-memory) and plug-in registration for embeddings/retrievers.
- Expose REST/gRPC services for ingestion and retrieval so external agents can integrate without importing Python modules.
- Instrument ingestion and maintenance with structured logging and metrics to support observability and alerting.
- Explore streaming ingestion pipelines (queues, webhooks) for near-real-time updates.
