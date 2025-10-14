# Agent Instructions

## Documentation Workflow
- After each batch of changes, add a `CHANGELOG.md` entry with an ISO 8601 date/time stamp and developer-facing detail (files, modules, functions, variables, and rationale). Every commit should correspond to a fresh entry.
- Maintain `README.md` as the canonical description of the project; update it whenever behaviour or workflows change. Archive older versions separately when requested.
- Keep the `docs/` wiki and provisioning guides (`SETUP.md`, `ENVIRONMENT_NEEDS.md`) in sync with code updates; add or revise the
  relevant page whenever features, modules, or workflows change.
- After each iteration, refresh `ISSUES.md`, `SOT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `TODO.md`, and related documentation to stay in sync with the codebase.
- Ensure `TODO.md` retains the `Completed`, `Priority Tasks`, and `Recommended Waiting for Approval Tasks` sections, moving finished items under `Completed` at the end of every turn.
- Make every task in `TODO.md` atomic: each entry must describe a single, self-contained deliverable with enough detail to execute and verify without cross-referencing additional context.
- Update `RESUME_NOTES.md` at the end of every turn so the next session starts with accurate context.
- When beginning a turn, review `README.md`, `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `ISSUES.md`, and `SOT.md` to harvest new actionable work. Maintain at least ten quantifiable, prioritised items in the `Priority Tasks` section of `TODO.md`, adding context or links when needed.
- After completing any task, immediately update `TODO.md`, check for the next actionable item, and continue iterating until all unblocked `Priority Tasks` are exhausted for the session.
- Continuously loop through planning and execution: finish a task, document it, surface new follow-ups, and resume implementation so long as environment blockers allow. If extra guidance would improve throughput, extend these instructions proactively.

## Style Guidelines
- Use descriptive Markdown headings starting at level 1 for top-level documents.
- Keep lines to 120 characters or fewer when practical.
- Prefer bullet lists for enumerations instead of inline commas.
