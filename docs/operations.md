# Operations & Maintenance

This guide covers operational tasks for MeshMind deployments.

## Configuration

- Environment variables are read via `meshmind.core.config.Settings`.
- Critical variables:
  - `GRAPH_BACKEND`: `memory`, `sqlite`, `neo4j`, or `memgraph`.
  - Connection URIs/usernames/passwords for Neo4j/Memgraph.
  - `SQLITE_PATH` when using the SQLite backend.
  - `REDIS_URL`, `OPENAI_API_KEY`, `EMBEDDING_MODEL` for optional integrations.
- `settings.missing()` groups missing variables by capability to simplify diagnostics.

## Bootstrap & Registries

- `meshmind.core.bootstrap.bootstrap_entities` ensures the `Memory` model is registered.
- `meshmind.core.bootstrap.bootstrap_encoders` primes default encoders (OpenAI if available).
- Registry state (entities/predicates) persists in process memory; configure the CLI/admin tasks to inspect/refresh when
  adding new schema types.

## Scheduled Tasks

- `meshmind.tasks.scheduled.run_consolidation_cycle`: consolidates duplicates using heuristics.
- `meshmind.tasks.scheduled.emit_importance_metrics`: records telemetry snapshots.
- All tasks rely on `MemoryManager.list_memories` and respect namespace/label filters for efficiency.

## Observability

- `meshmind.core.observability.telemetry` exposes counters and gauges with `snapshot()` for inspection.
- The `docs/telemetry.md` page lists the available metrics and logging patterns.

## Admin CLI

- `meshmind.cli.admin` provides commands to:
  - Validate backend connectivity (Neo4j/Memgraph/SQLite).
  - Run consolidation plans manually.
  - Inspect registry contents.
  - Summarize configuration with sensitive values masked.

## Deployment Considerations

- Provision graph databases externally (Docker, managed service) and expose Bolt endpoints reachable from the runtime.
- Ensure optional dependencies (`neo4j`, `mgclient`, `redis`, `celery`, `tiktoken`) are installed where required.
- Configure logging/metrics sinks to capture telemetry emitted by pipeline stages.
- Use `docker-compose.yml` as a reference for local orchestration (Memgraph, Redis, API services).
