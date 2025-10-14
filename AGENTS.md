# Agent Instructions

## Documentation Workflow
- After each batch of changes, add a `CHANGELOG.md` entry with an ISO 8601 date/time stamp and developer-facing detail (files, modules, functions, variables, and rationale). Every commit should correspond to a fresh entry.
- Maintain `README.md` as the canonical description of the project; update it whenever behaviour or workflows change. Archive older versions separately when requested.
- Keep the `docs/` wiki in sync with code updates; add or revise the relevant page whenever features, modules, or workflows change.
- After each iteration, refresh `ISSUES.md`, `SOT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `TODO.md`, and related documentation to stay in sync with the codebase.
- Ensure `TODO.md` retains the `Completed`, `Priority Tasks`, and `Recommended Waiting for Approval Tasks` sections, moving finished items under `Completed` at the end of every turn.
- Update `RESUME_NOTES.md` at the end of every turn so the next session starts with accurate context.

## Style Guidelines
- Use descriptive Markdown headings starting at level 1 for top-level documents.
- Keep lines to 120 characters or fewer when practical.
- Prefer bullet lists for enumerations instead of inline commas.
