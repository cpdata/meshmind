# Agent Instructions

## Beads Issue Tracking
- Use the `bd` Beads CLI for all issue, task, and dependency tracking in this repository.
- Keep every issue up to date: assign `codex` when the work is agent-owned, `human` when it requires external help, and maintain `area/*`, `priority/*`, and `status/blocked` labels so filtering remains useful.
- Immediately capture newly discovered work or blockers in Beads before continuing implementation, and wire dependencies (`bd dep add`) so `bd ready` only lists actionable tasks.
- If the `.beads/` database is missing, run `bd init` (and `bd import -i .beads/issues.jsonl` if needed) and commit the resulting files.

## Iteration Workflow
- Begin each session with `bd ready`/`bd list --status open` to understand available work and outstanding blockers.
- Close or update issues as soon as changes land, and keep dependency graphs accurate so downstream tasks stay blocked until prerequisites resolve.
- Add an entry to `CHANGELOG.md` for every change set with an ISO 8601 timestamp in America/New_York summarizing developer-facing impact and rationale.
- Rely on Beads for planning instead of sprawling Markdown checklists; use docs only for long-lived guidance that end users need.

## Documentation & Communication
- Update `README.md`, `docs/`, and provisioning guides only when the implementation meaningfully changes behaviour or workflows touched by the turn.
- Keep high-level orientation docs (`ISSUES.md`, `PLAN.md`, `ROADMAP.md`, `RECOMMENDATIONS.md`) short and reference the relevant Beads issue IDs instead of duplicating task lists.
- Maintain `RESUME_NOTES.md` at the end of each turn so the next session starts with accurate context.

## bd quickstart reference output
```
bd - Dependency-Aware Issue Tracker

Issues chained together like beads.

GETTING STARTED
  bd init   Initialize bd in your project
            Creates .beads/ directory with project-specific database
            Auto-detects prefix from directory name (e.g., myapp-1, myapp-2)

  bd init --prefix api   Initialize with custom prefix
            Issues will be named: api-1, api-2, ...

CREATING ISSUES
  bd create "Fix login bug"
  bd create "Add auth" -p 0 -t feature
  bd create "Write tests" -d "Unit tests for auth" --assignee alice

VIEWING ISSUES
  bd list       List all issues
  bd list --status open  List by status
  bd list --priority 0  List by priority (0-4, 0=highest)
  bd show bd-1       Show issue details

MANAGING DEPENDENCIES
  bd dep add bd-1 bd-2     Add dependency (bd-2 blocks bd-1)
  bd dep tree bd-1  Visualize dependency tree
  bd dep cycles      Detect circular dependencies

DEPENDENCY TYPES
  blocks  Task B must complete before task A
  related  Soft connection, doesn't block progress
  parent-child  Epic/subtask hierarchical relationship
  discovered-from  Auto-created when AI discovers related work

READY WORK
  bd ready       Show issues ready to work on
            Ready = status is 'open' AND no blocking dependencies
            Perfect for agents to claim next work!

UPDATING ISSUES
  bd update bd-1 --status in_progress
  bd update bd-1 --priority 0
  bd update bd-1 --assignee bob

CLOSING ISSUES
  bd close bd-1
  bd close bd-2 bd-3 --reason "Fixed in PR #42"

DATABASE LOCATION
  bd automatically discovers your database:
    1. --db /path/to/db.db flag
    2. $BEADS_DB environment variable
    3. .beads/*.db in current directory or ancestors
    4. ~/.beads/default.db as fallback

AGENT INTEGRATION
  bd is designed for AI-supervised workflows:
    • Agents create issues when discovering new work
    • bd ready shows unblocked work ready to claim
    • Use --json flags for programmatic parsing
    • Dependencies prevent agents from duplicating effort

DATABASE EXTENSION
  Applications can extend bd's SQLite database:
    • Add your own tables (e.g., myapp_executions)
    • Join with issues table for powerful queries
    • See database extension docs for integration patterns:
      https://github.com/steveyegge/beads/blob/main/EXTENDING.md

GIT WORKFLOW (AUTO-SYNC)
  bd automatically keeps git in sync:
    • ✓ Export to JSONL after CRUD operations (5s debounce)
    • ✓ Import from JSONL when newer than DB (after git pull)
    • ✓ Works seamlessly across machines and team members
    • No manual export/import needed!
  Disable with: --no-auto-flush or --no-auto-import

Ready to start!
Run bd create "My first issue" to create your first issue.
```
