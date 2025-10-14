# Development Workflow

This guide summarizes expectations when contributing to MeshMind.

## Prerequisites

- Python 3.11 or 3.12 is recommended (see `pyproject.toml`).
- Install dependencies with `pip install -e .[dev]`.
- Optional extras: `neo4j`, `mgclient`, `redis`, `celery`, `tiktoken`, `python-dotenv`.

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
- The Makefile includes shortcuts (`make test`, `make lint`, `make format`) for local validation.
- CI also executes `make docs-guard` so missing documentation updates will fail the pipeline.
