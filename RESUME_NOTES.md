# Resume Notes

## Current Context

- Branch: `work`.
- Optional dependencies are now first-class: `pyproject.toml` installs REST (`fastapi`, `uvicorn`), graph (`neo4j`, `mgclient`,
  `redis`), and dev extras by default, and the Makefile’s `install` target installs `.[dev,docs,testing]`.
- Docker assets have been expanded: the root `docker-compose.yml` runs Memgraph, Neo4j, and Redis with health checks, and
  `meshmind/tests/docker/` contains targeted stacks for integration scenarios. A new `Dockerfile` supports worker containers.
- Provisioning guidance lives in `SETUP.md`, `ENVIRONMENT_NEEDS.md`, and `NEEDED_FOR_TESTING.md`; docs guard now tracks these
  guides when related modules change.

## Latest Changes

- Added the dependency extras above, updated `.github/workflows/ci.yml` to use `uv pip install --system`, and refreshed
  onboarding docs (`README.md`, `docs/`, `PROJECT.md`, `PLAN.md`, `SOT.md`, `FINDINGS.md`, `RECOMMENDATIONS.md`,
  `ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`) to reference the new workflow and credentials.
- Replaced the old docker-compose stack with multi-service definitions, introduced per-topology Compose files under
  `meshmind/tests/docker/`, authored `SETUP.md`, and documented the stack in README/docs.
- Extended `scripts/check_docs_sync.py` and its pytest coverage so changes under `meshmind/tests/docker/`, `docker-compose.yml`,
  or the `Dockerfile` require updates to `SETUP.md`, `ENVIRONMENT_NEEDS.md`, or the operations docs.
- Restored the missing `argparse` import in `meshmind/cli/admin.py` so admin subcommands register correctly.
- Ran the full pytest suite (69 tests) to confirm the refactor passes without external services.

## Environment State

- External services (Neo4j, Memgraph, Redis) remain unavailable; tests rely on fakes and SQLite/in-memory drivers.
- Outbound package downloads are blocked (`pip install uv` returns HTTP 403 via the proxy), preventing regeneration of
  `uv.lock`. The need for PyPI access is recorded in `ISSUES.md` and `ENVIRONMENT_NEEDS.md`.
- Optional packages (`neo4j`, `mgclient`, `redis`, `celery`, `tiktoken`, `sentence-transformers`) are still absent locally.

## Next Session Starting Points

1. Address the `TODO.md` priority backlog—top items are regenerating `uv.lock` once network access is restored and validating the
   new docs guard paths; remaining work focuses on live Neo4j/Memgraph validation, consolidation tuning, and proto generation.
2. When network/infrastructure unblockers land, install the optional dependencies and spin up the compose stacks to validate
   driver connectivity and REST/gRPC smoke tests.
3. Continue expanding backend-native vector search and importance-evaluation loops once larger datasets and live services are
   available.
4. Keep `SETUP.md`, `ENVIRONMENT_NEEDS.md`, and the wiki in sync with any further tooling or configuration adjustments and update
   this file at the end of each session.

## Helpful References

- `docs/overview.md` for the high-level module map.
- `docs/persistence.md` and `docs/operations.md` for backend specifics and operational runbooks.
- `SETUP.md` for provisioning instructions; `ENVIRONMENT_NEEDS.md` for outstanding environment requests.
- `ISSUES.md` and `TODO.md` for the live backlog and blockers.
