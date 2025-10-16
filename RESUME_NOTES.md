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

- Generated protobuf modules (`meshmind/protos/memory_service.proto`) now back the gRPC stub; tests and docs were updated to reference the canonical schema instead of dataclasses.
- Added a `make benchmarks` target that executes the synthetic benchmarking scripts and stores JSON output under `build/benchmarks/`, with documentation updates in `docs/testing.md` and `README.md`.
- Refreshed planning and environment docs (`PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `FINDINGS.md`, `ISSUES.md`, `ENVIRONMENT_NEEDS.md`, `NEEDED_FOR_TESTING.md`, `CLEANUP.md`, `DUMMIES.md`, `ROADMAP.md`) to capture the protobuf integration and benchmarking workflow.

## Environment State

- External graph services (Neo4j, Memgraph) and Redis are still unavailable inside this sandbox; integration tests depend on
  fakes or SQLite until infrastructure is provisioned.
- Internet access is currently available; optional packages (`neo4j`, `pymgclient`, `fastapi`, `uvicorn`, etc.) are installed
  via `uv pip`. Maintain this access so `uv.lock` can be regenerated and provisioning scripts remain effective.
- Timezone defaults across pipeline utilities now emit timezone-aware UTC timestamps; existing persisted data should be
  reviewed once live backends are in play.

## Next Session Starting Points

1. Work through the remaining `TODO.md` priority items (Neo4j validation, backend-native vector search, benchmarking against live backends, regenerating locks). Add follow-up tasks as new discoveries surface.
2. Validate Neo4j connectivity end-to-end once a reachable instance is available, using `meshmind admin graph --backend neo4j` and the docker-compose stack.
3. Run the new benchmarking scripts against production-sized or synthetic datasets hosted externally to calibrate maintenance retry defaults and document recommended values in `ENVIRONMENT_NEEDS.md` / `README.md`.
4. Promote the protobuf-backed gRPC stub into a real server once infrastructure is available, then add end-to-end tests using a live channel.
5. Push vector similarity into Memgraph/Neo4j or document fallback limitations once native index strategies are available; continue updating `docs/api.md`/`docs/retrieval.md` with findings.

## Helpful References

- `docs/overview.md` for the module map and terminology.
- `docs/configuration.md` and `docs/operations.md` for environment variables and provisioning details.
- `SETUP.md`, `ENVIRONMENT_NEEDS.md`, and `NEEDED_FOR_TESTING.md` for onboarding and infrastructure expectations.
- `TODO.md` and `ISSUES.md` for the prioritized backlog and outstanding blockers.
