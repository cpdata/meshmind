# Agent Instructions

## Issue Tracking with Beads
- Use the `bd` Beads CLI for all issue, task, and dependency tracking in this repository.
- Initialize the tracker with `bd init` if the `.beads/` database is missing, and commit the resulting files.
- When you discover new work, blockers, or follow-ups while coding, immediately create a Beads issue before continuing the task at hand.
- Keep issue metadata accurate: set priorities, statuses, and dependency edges (`blocks`, `related`, `parent-child`, `discovered-from`) so the ready queue always reflects the next actionable work.
- Review available work with `bd ready`/`bd list` at the start of each session, and close or update issues as soon as the underlying work lands.

## Documentation Workflow
- After each batch of changes, add a `CHANGELOG.md` entry with an ISO 8601 timestamp in United States Eastern time (e.g., `America/New_York`) summarising developer-facing details and rationale.
- Maintain `README.md` as the canonical description of the project; update it whenever behaviour or workflows change. Archive older versions separately when requested.
- Keep the `docs/` wiki and provisioning guides (`SETUP.md`, `ENVIRONMENT_NEEDS.md`) in sync with code updates; revise the relevant page whenever features, modules, or workflows change.
- After each iteration, refresh `ISSUES.md`, `SOT.md`, `PLAN.md`, and `RECOMMENDATIONS.md` so they stay aligned with the current state of the codebase and Beads issue tracker.
- Update `RESUME_NOTES.md` at the end of every turn so the next session starts with accurate context.
- When beginning a turn, review `README.md`, `PROJECT.md`, `PLAN.md`, `RECOMMENDATIONS.md`, `ISSUES.md`, `SOT.md`, `ROADMAP.md`, `PLANNING_THOUGHTS.md`, the `research/` wiki, and the open Beads issues to harvest actionable work.
- Keep `ROADMAP.md`, `PLANNING_THOUGHTS.md`, and the `research/` docs aligned with each iteration when new discoveries or decisions occur.
- Continuously loop through planning and execution: finish a task, document it, surface new follow-ups as Beads issues, and resume implementation while unblocked work remains.

## Style Guidelines
- Use descriptive Markdown headings starting at level 1 for top-level documents.
- Keep lines to 120 characters or fewer when practical.
- Prefer bullet lists for enumerations instead of inline commas.

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
