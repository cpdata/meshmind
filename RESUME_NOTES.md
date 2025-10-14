# Resume Notes

## Current Context

- Branch: `work`.
- Optional dependencies remain enumerated in `pyproject.toml` with extras that cover REST (`fastapi`, `uvicorn`), graph drivers
  (`neo4j`, `pymgclient`, `redis`), and developer tooling (`ruff`, `pyright`, docs toolchain). `Makefile install` still targets
  `.[dev,docs,testing]`.
- Docker orchestration (root `docker-compose.yml` plus `meshmind/tests/docker/*.yml`) provisions Memgraph, Neo4j, Redis, and
  optional Celery workers. The `Dockerfile` supports bespoke worker images.
- Provisioning references live in `SETUP.md`, `ENVIRONMENT_NEEDS.md`, and `NEEDED_FOR_TESTING.md`; docs guard enforces updates
  when infrastructure assets change.

## Latest Changes

- Authored `run/install_setup.sh` and `run/maintenance_setup.sh` to automate package installation (apt + `uv pip sync`) for
  fresh and cached environments; both scripts assume outbound network access and sudo privileges.
- Updated `README.md` and `SETUP.md` to reference the automation scripts, noted their requirements in `SOT.md`, and refreshed
  roadmap docs (`PLAN.md`, `RECOMMENDATIONS.md`, `ISSUES.md`) to track the upcoming LLM provider abstraction effort.
- Added an atomic-task rule to `AGENTS.md` and rewrote `TODO.md`’s priority section: new top items cover drafting `CLEANUP.md`,
  introducing a configurable `meshmind/llm_client.py`, and wiring cascading LLM overrides through configuration, CLI, and API
  surfaces.
- Documented outstanding work in `ISSUES.md` (LLM client refactor, consolidation validation) so blockers remain visible once
  infrastructure is available.
- Confirmed outbound network access, installed optional dependencies (`neo4j`, `pymgclient`, `redis`, REST/LLM tooling) via `uv pip install`,
  and updated documentation plus dependency metadata (`pyproject.toml`, environment guides) to reference `pymgclient` as the Memgraph driver package.
- Ran `pytest` successfully with the expanded dependency set to confirm optional installations keep the suite green.

## Environment State

- External services (Neo4j, Memgraph, Redis) remain unavailable; tests rely on fakes and SQLite/in-memory drivers.
- Outbound package downloads now succeed (confirmed via `uv pip install` for optional dependencies); keep the network channel
  open so `uv lock` regeneration can proceed next session.
- Optional packages (`neo4j`, `pymgclient`, `redis`, `celery`, `tiktoken`, `sentence-transformers`) are installed in this
  sandbox via `uv pip install`; rerun the `run/` scripts to keep cached images current and apply updates during maintenance.

## Next Session Starting Points

1. Start with the top `TODO.md` priorities next session (after internet access arrives): draft `CLEANUP.md`, build the
   provider-agnostic `meshmind/llm_client.py`, replace direct OpenAI usage, and add cascading override support across config,
   CLI, and API layers. Tests/docs must be updated alongside the refactor.
2. Once network access is restored, run `./run/install_setup.sh` (fresh) or `./run/maintenance_setup.sh` (cache refresh) to
   install optional dependencies, then regenerate `uv.lock` and validate the docs guard/CI workflows under the new dependency
   stack.
3. Revisit the remaining backlog items—live Neo4j/Memgraph connectivity, consolidation heuristics on large datasets, proto
   generation, backend-native vector search—after the LLM client refactor and dependency sync are complete.
4. Continue synchronizing `README.md`, `SETUP.md`, `docs/`, and planning files with code changes; update `RESUME_NOTES.md` at the
   end of each session.

## Helpful References

- `docs/overview.md` for the high-level module map.
- `docs/persistence.md` and `docs/operations.md` for backend specifics and operational runbooks.
- `SETUP.md` for provisioning instructions; `ENVIRONMENT_NEEDS.md` for outstanding environment requests.
- `ISSUES.md` and `TODO.md` for the live backlog and blockers.
