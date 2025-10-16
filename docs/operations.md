# Operations & Maintenance

This guide covers operational tasks for MeshMind deployments.

## Configuration

- Environment variables are read via `meshmind.core.config.Settings`.
- Critical variables:
  - `GRAPH_BACKEND`: `memory`, `sqlite`, `neo4j`, or `memgraph`.
  - Connection URIs/usernames/passwords for Neo4j/Memgraph.
  - `SQLITE_PATH` when using the SQLite backend.
  - `REDIS_URL`, `LLM_API_KEY`/`OPENAI_API_KEY`, and the `LLM_*` model/base URL overrides for optional LLM integrations.
- `settings.missing()` groups missing variables by capability to simplify diagnostics.

## Provisioning Scripts

- `run/install_setup.sh` installs system packages, ensures `uv` is available, validates that optional dependencies
  (`fastapi`, `neo4j`, `pymgclient`, `uvicorn`) are declared in `pyproject.toml`, and syncs Python requirements from
  `uv.lock` when present. Use `MESH_SKIP_SYSTEM_PACKAGES=1` and/or `MESH_SKIP_PYTHON_SYNC=1` to perform a validation-only run
  when network access is unavailable.
- `run/maintenance_setup.sh` refreshes cached environments with the same validation logic and respects the same skip flags so
  CI can dry-run provisioning.

## Bootstrap & Registries

- `meshmind.core.bootstrap.bootstrap_entities` ensures the `Memory` model is registered.
- `meshmind.core.bootstrap.bootstrap_encoders` primes default encoders via the provider-agnostic `LLMClient` when available.
- Registry state (entities/predicates) persists in process memory; configure the CLI/admin tasks to inspect/refresh when
  adding new schema types.

## Scheduled Tasks

- `meshmind.tasks.scheduled.expire_task`: prunes expired memories based on TTL metadata.
- `meshmind.tasks.scheduled.consolidate_task`: merges duplicates, persists consolidation results, emits telemetry, and retries
  conflicting writes using exponential backoff (`MAINTENANCE_MAX_ATTEMPTS`, `MAINTENANCE_BASE_DELAY_SECONDS`). Conflicts and
  retry durations are logged for later analysis.
- `meshmind.tasks.scheduled.compress_task`: re-compresses long memories and persists updates to the configured backend.
- All tasks rely on `MemoryManager.list_memories` and respect namespace/label filters for efficiency.

## Observability

- `meshmind.core.observability.telemetry` exposes counters and gauges with `snapshot()` for inspection.
- The `docs/telemetry.md` page lists the available metrics and logging patterns.

## Admin CLI

- `meshmind.cli.admin` provides commands to:
  - Validate backend connectivity (Neo4j/Memgraph/SQLite).
  - Summarize stored memories via `mesh admin counts --namespace <ns>` grouped by entity label.
  - Run consolidation plans manually.
  - Inspect registry contents.
  - Summarize configuration with sensitive values masked.
  Automated smoke tests exercise the `/memories/counts` REST endpoint and the CLI counts command using the in-memory driver so
  documentation stays in sync with working behaviour.

## Deployment Considerations

- Provision graph databases externally (Docker, managed service) and expose Bolt endpoints reachable from the runtime.
- Ensure optional dependencies (`neo4j`, `pymgclient`, `redis`, `celery`, `fastapi`, `uvicorn`, `tiktoken`) are installed where required (or install `.[dev,docs,testing]`).
- Configure logging/metrics sinks to capture telemetry emitted by pipeline stages.
- Use `docker-compose.yml` as a reference for local orchestration (Memgraph, Neo4j, Redis) and the targeted stacks in `meshmind/tests/docker/` for integration testing.
