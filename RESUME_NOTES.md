# Resume Notes

## Current Context

- Branch: `integration-updates` (target PR branch: `integration`).
- Optional dependencies are bundled in the `.[dev,docs,testing]` extras, covering REST (`fastapi`, `uvicorn`), graph drivers
  (`neo4j`, `pymgclient`, `redis`), Celery, LLM tooling, and developer linters. The provisioning scripts under `run/`
  synchronize from `uv.lock` and verify these extras before attempting installs.
- Docker orchestration (root `docker-compose.yml` and the files in `meshmind/tests/docker/`) provisions Memgraph, Neo4j, Redis,
  and optional Celery workers. Keep these references handy for live integration testing once container access is available.
- Documentation guard tooling requires that code edits touching modules with wiki pages also update the relevant files in
  `docs/`. Planning artifacts (`PLAN.md`, `PROJECT.md`, `SOT.md`, `ROADMAP.md`, `PLANNING_THOUGHTS.md`) and the new `research/`
  wiki are refreshed every iteration per agent instructions.

## Latest Changes

- Created strategic references (`ROADMAP.md`, `PLANNING_THOUGHTS.md`, `research/overview.md`) to capture milestones, decision
  context, and competitor analysis alongside the existing planning docs.
- Added configurable maintenance retry controls (`MAINTENANCE_MAX_ATTEMPTS`, `MAINTENANCE_BASE_DELAY_SECONDS`) and implemented
  exponential backoff for consolidation/compression writes. Updated `README.md`, `docs/configuration.md`, `docs/operations.md`,
  `docs/telemetry.md`, and `SOT.md` to describe the new behaviour and metrics.
- Introduced REST/CLI smoke coverage for `/memories/counts` via `meshmind/tests/test_counts_smoke.py` and expanded maintenance
  tests in `meshmind/tests/test_tasks_scheduled.py` to assert retry semantics. `docs/testing.md` now highlights the new suites.
- Refreshed `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`, `ISSUES.md`, `ENVIRONMENT_NEEDS.md`,
  `NEEDED_FOR_TESTING.md`, and `RESUME_NOTES.md` to align with the retry controls, new docs, and expanded smoke coverage.

## Environment State

- External graph services (Neo4j, Memgraph) and Redis are still unavailable inside this sandbox; integration tests depend on
  fakes or SQLite until infrastructure is provisioned.
- Internet access is currently available; optional packages (`neo4j`, `pymgclient`, `fastapi`, `uvicorn`, etc.) are installed
  via `uv pip`. Maintain this access so `uv.lock` can be regenerated and provisioning scripts remain effective.
- Timezone defaults across pipeline utilities now emit timezone-aware UTC timestamps; existing persisted data should be
  reviewed once live backends are in play.

## Next Session Starting Points

1. Work through the remaining `TODO.md` priority items (Neo4j validation, heuristic evaluation loops, gRPC definitions, backend-native vector search). Add follow-up tasks as new discoveries surface.
2. Validate Neo4j connectivity end-to-end once a reachable instance is available, using `meshmind admin graph --backend neo4j` and the docker-compose stack.
3. Benchmark consolidation heuristics with larger datasets to tune the new maintenance retry defaults and record recommended values in `ENVIRONMENT_NEEDS.md` / `README.md`.
4. Plan integration tests for LLM override payloads and counts endpoints against live REST/gRPC deployments when credentials and infrastructure are provisioned; update docs/testing accordingly.
5. Continue chipping away at shim retirements documented in `DUMMIES.md`—prioritise reintroducing real Pydantic models once packaging constraints are resolved.

## Helpful References

- `docs/overview.md` for the module map and terminology.
- `docs/configuration.md` and `docs/operations.md` for environment variables and provisioning details.
- `SETUP.md`, `ENVIRONMENT_NEEDS.md`, and `NEEDED_FOR_TESTING.md` for onboarding and infrastructure expectations.
- `TODO.md` and `ISSUES.md` for the prioritized backlog and outstanding blockers.
