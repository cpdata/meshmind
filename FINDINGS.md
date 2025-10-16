# Findings

## General Observations
- Core modules are now wired through the `MeshMind` client, including CRUD, triplet storage, and retrieval helpers. Graph-backed wrappers fetch namespace/entity-label filtered candidates from the configured driver automatically; remaining integration work focuses on server-side query optimisation and heuristic evaluation loops.
- Optional dependencies are largely guarded behind lazy imports, compatibility shims, or factory functions, improving portability. Environments still need to install tooling referenced by the Makefile and CI (ruff, pyright, typeguard, toml-sort, yamllint). `DUMMIES.md` now tracks every shim so we can retire them as integration coverage expands.
- LLM usage is now centralized in `meshmind.llm_client` with per-operation defaults cascading from `LLM_*` environment variables and CLI overrides, reducing the risk of divergent configurations across pipelines and retrieval. REST/gRPC payloads now provide matching override dictionaries so services can experiment per request.
- Timestamp helpers default to timezone-aware UTC, eliminating naive datetime outputs that previously leaked into maintenance pipelines and compatibility shims.
- Documentation artifacts (`README.md`, `SOT.md`, `ENVIRONMENT_NEEDS.md`, `docs/`) stay current when updated with each iteration; the legacy README has been archived as `README_OLD.md`. A docs-guard script now enforces synchronized updates during CI.

## Dependency & Environment Notes
- `MeshMind` defers driver creation until persistence is required, enabling workflows without the `mgclient` module (install `pymgclient` to obtain it) and selecting between
  in-memory, SQLite, Memgraph, or Neo4j backends. CLI helpers (`meshmind admin graph`) now expose connectivity sanity checks.
- Package management via `uv` now succeeds (optional dependencies installed via `uv pip install` this session); keep network access available so `uv.lock` regeneration can proceed when prioritized. Provisioning scripts (`run/install_setup.sh`, `run/maintenance_setup.sh`) now validate optional extras and support dry-run mode, with pytest coverage ensuring the flags continue to behave.
- Project metadata now advertises Python `>=3.11,<3.13`, aligning with available wheels for optional dependencies.
- Encoder registration occurs during bootstrap, but custom deployments must ensure compatible models are registered before
  extraction or hybrid search.
- The OpenAI embedding adapter still expects dictionary-like responses; adapting to SDK objects remains on the backlog.
- Repository audit confirmed there are no lingering `import openai` statements outside guarded sections; the client and
  embedding modules already encapsulate the SDK behind optional imports, easing the upcoming refactor to a dedicated
  wrapper.
- Celery tasks initialize lazily, yet Redis/Memgraph services are still required at runtime. Docker Compose now provisions
  Memgraph, Neo4j, and Redis, while targeted stacks under `meshmind/tests/docker/` support integration testing. `SETUP.md`
  explains provisioning and teardown commands.

## Data Flow & Persistence
- Triplet storage now persists relationships and tracks predicates automatically, closing an earlier data-loss gap.
- Consolidation and compression utilities now persist updates through the maintenance tasks, enforce configurable exponential backoff (`MAINTENANCE_MAX_ATTEMPTS`, `MAINTENANCE_BASE_DELAY_SECONDS`), and surface skipped groups; larger-scale validation remains necessary.
- Importance scoring uses heuristics (token diversity, recency, metadata richness, embedding magnitude) and now records telemetry summaries; continued evaluation will raise retrieval quality.

## CLI & Tooling
- CLI ingestion bootstraps encoders and entities automatically and now ships `admin` subcommands for predicate maintenance, telemetry dumps, graph connectivity checks, and namespace/entity counts. Automated smoke tests cover the counts workflow end-to-end using the in-memory driver. External backends still require valid credentials and running services.
- The Makefile introduces lint, format, type-check, test, and docs-guard targets, plus Docker helpers. External tooling installation is
  required before targets succeed.
- GitHub Actions now run formatting checks, the docs guard, and pytest on push/PR, providing basic CI coverage.

## Testing & Quality
- Pytest suites rely on fixtures (`memory_factory`, `dummy_encoder`) and compatibility shims to run without external services. Coverage now includes graph-backed retrieval wrappers, Neo4j connectivity shims, CLI admin flows, counts smoke tests, docs guard checks, and Celery consolidation telemetry/backoff handling.
- Type checking via `pyright` and runtime checks via `typeguard` are exposed in the Makefile; dependency installation is
  necessary for full validation.

## Documentation
- `README.md` documents setup, pipelines, retrieval, tooling, service interfaces, observability, and the new maintenance retry controls.
- Strategic documentation (`ROADMAP.md`, `PLANNING_THOUGHTS.md`, `research/overview.md`) summarises milestones, decision context, and competitor analysis for future planning.
- Supporting docs (`ISSUES.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `SOT.md`) reflect the latest capabilities and highlight remaining
  gaps, aiding onboarding and future planning.
