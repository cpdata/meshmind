# Development Workflow

This guide summarizes expectations when contributing to MeshMind.

## Prerequisites

- Python 3.11 or 3.12 is recommended (see `pyproject.toml`).
- Install dependencies with `uv sync --all-extras` (preferred) or `pip install -e .[dev,docs,testing]` if `uv` is unavailable; drop
  `--system` when using an activated virtualenv.
- Optional extras: none—`.[dev,docs,testing]` pulls in REST tooling (`fastapi`, `uvicorn`), graph drivers (`neo4j`, `pymgclient`,
  `redis`), LLM tooling (`openai`, `tiktoken`, `sentence-transformers`), and developer utilities. Refer to `SETUP.md` for
  service provisioning steps.

## Coding Standards

- Follow the style rules documented in `AGENTS.md` (120-character lines, meaningful headings, bullet lists for
  enumerations).
- Keep code modular and dependency-light to maintain deterministic tests.
- Avoid wrapping imports in `try/except` unless explicitly handling optional dependencies.

## Documentation

- Update `README.md`, `CHANGELOG.md`, `docs/`, `SOT.md`, and other root markdown files whenever behaviour changes.
- Each change batch must append a timestamped entry to `CHANGELOG.md` describing modules, functions, and rationale.
- Maintain `RESUME_NOTES.md` at the end of every turn to capture context for future sessions.
- Run `make docs-guard` (optionally with `BASE_REF=<ref>`) before pushing to ensure code changes have matching documentation updates.

## Pydantic Model Policy

- MeshMind now requires `pydantic>=2.12` and targets Python 3.11–3.12. Compatibility shims have been removed; all new models
  must subclass the native Pydantic 2 `BaseModel`.
- Maintain parity with the latest 2.x minor releases and plan to refresh the lockfile quarterly once upstream publishes wheels
  for Python 3.13. Until then, enforce `.python-version` <= 3.12 in the repo.
- When introducing breaking model changes, update REST/gRPC payloads and integration tests concurrently and record migration
  notes in `CHANGELOG.md` and release documentation.

## Testing

- Run `pytest` before committing.
- Add unit tests for new features, especially when touching drivers, pipelines, or retrieval logic.
- Use the fake drivers and fixtures to avoid requiring external services.

## Git Workflow

- Work on feature branches derived from the current branch (e.g., `work`).
- Commit logically grouped changes with descriptive messages.
- Generate PR summaries via the automated tooling once commits are ready.

## Continuous Integration

- `.github/workflows/ci.yml` runs linting and tests; ensure new code paths are covered.
- The Makefile includes shortcuts (`make test`, `make lint`, `make format`, `make protos`, `make protos-check`) for local validation.
- CI also executes `make docs-guard` and `make protos-check` so missing documentation updates or out-of-date protobuf bindings
  will fail the pipeline.
