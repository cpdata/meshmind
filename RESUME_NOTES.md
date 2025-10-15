# Resume Notes

## Current Context

- Branch: `work` (target PR branch: `integration`).
- Optional dependencies are bundled in the `.[dev,docs,testing]` extras, covering REST (`fastapi`, `uvicorn`), graph drivers
  (`neo4j`, `pymgclient`, `redis`), Celery, LLM tooling, and developer linters. The provisioning scripts under `run/`
  synchronize from `uv.lock` and verify these extras before attempting installs.
- Docker orchestration (root `docker-compose.yml` and the files in `meshmind/tests/docker/`) provisions Memgraph, Neo4j, Redis,
  and optional Celery workers. Keep these references handy for live integration testing once container access is available.
- Documentation guard tooling requires that code edits touching modules with wiki pages also update the relevant files in
  `docs/`. Planning artifacts (`PLAN.md`, `PROJECT.md`, `SOT.md`, etc.) are refreshed every iteration per agent instructions.

## Latest Changes

- Documented the LLM override cascade across `README.md`, `docs/api.md`, and `docs/configuration.md`, including precedence
  notes and example payloads/CLI flags.
- Updated operations guides (`SETUP.md`, `docs/operations.md`) to describe the provisioning script validation flow and skip
  flags; highlighted the pytest smoke tests that cover these scripts.
- Refreshed planning/backlog documents (`SOT.md`, `PLAN.md`, `PROJECT.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`, `ISSUES.md`)
  with timezone-aware timestamp notes and the new per-request override workflow.
- Extended `DUMMIES.md` and `docs/testing.md` to capture the `FakeLLMClient` behaviour and the setup script smoke-test
  coverage; updated `ENVIRONMENT_NEEDS.md` and `NEEDED_FOR_TESTING.md` to acknowledge that optional packages now install with
  network access.

## Environment State

- External graph services (Neo4j, Memgraph) and Redis are still unavailable inside this sandbox; integration tests depend on
  fakes or SQLite until infrastructure is provisioned.
- Internet access is currently available; optional packages (`neo4j`, `pymgclient`, `fastapi`, `uvicorn`, etc.) are installed
  via `uv pip`. Maintain this access so `uv.lock` can be regenerated and provisioning scripts remain effective.
- Timezone defaults across pipeline utilities now emit timezone-aware UTC timestamps; existing persisted data should be
  reviewed once live backends are in play.

## Next Session Starting Points

1. Work through the remaining `TODO.md` priority items that are unblocked by missing infrastructure (e.g., research tasks may
   remain pending until live services exist).
2. Validate Neo4j connectivity end-to-end once a reachable instance is available, using `meshmind admin graph --backend neo4j`.
3. Plan integration tests for the LLM override payloads against a real provider when credentials are provisioned; update
   `docs/testing.md` accordingly.
4. Continue chipping away at shim retirements documented in `DUMMIES.md`, starting with replacing the Pydantic compatibility
   layer when production targets allow the real dependency.

## Helpful References

- `docs/overview.md` for the module map and terminology.
- `docs/configuration.md` and `docs/operations.md` for environment variables and provisioning details.
- `SETUP.md`, `ENVIRONMENT_NEEDS.md`, and `NEEDED_FOR_TESTING.md` for onboarding and infrastructure expectations.
- `TODO.md` and `ISSUES.md` for the prioritized backlog and outstanding blockers.
