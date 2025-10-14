# Resume Notes

## Current Context

- Branch: `work`.
- Graph drivers support namespace and entity-label filtering via the updated `GraphDriver.list_entities` contract.
- REST/gRPC services and the MeshMind client surface `entity_labels` arguments so searches and CRUD operations hydrate
  only relevant memory types.
- Documentation has been reorganized into `docs/` to mirror project modules; all root markdown files require updates when
  behaviour changes.

## Latest Changes

- Added driver-level filtering and propagated it through `MemoryManager`, retrieval helpers, and service interfaces.
- Expanded tests (`test_graph_retrieval`, `test_service_interfaces`, `test_pipeline_preprocess_store`) to validate the
  new filtering semantics and REST/gRPC compatibility.
- Created developer wiki pages under `docs/` and authored `ENVIRONMENT_NEEDS.md` for provisioning requests.
- Removed the redundant `NEW_README.md` in favour of the canonical `README.md`.

## Environment State

- External services (Neo4j, Memgraph, Redis) are not currently available inside this sandbox; testing relies on fakes.
- Optional packages (`neo4j`, `mgclient`, `redis`, `celery`, `tiktoken`) remain uninstalled—see `ENVIRONMENT_NEEDS.md`.

## Next Session Starting Points

1. Review `TODO.md` -> `Priority Tasks` for the ordered backlog (ensured to contain at least 10 actionable items).
2. Execute outstanding tasks that do not require external services (e.g., deeper analytics on heuristics, docs polish).
3. Once the environment updates arrive, prioritize integration tests against real Neo4j/Memgraph instances and Redis
   caching flows.
4. Update `CHANGELOG.md`, `README.md`, and `docs/` after every change; close the loop by refreshing `RESUME_NOTES.md`.

## Helpful References

- `docs/overview.md` for the high-level module map.
- `docs/persistence.md` for driver details and configuration tips.
- `ENVIRONMENT_NEEDS.md` for provisioning checklist.
- `ISSUES.md` and `TODO.md` for the live issue backlog.
