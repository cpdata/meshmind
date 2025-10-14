# Persistence Layer

MeshMind persists memories and triplets through interchangeable graph drivers. Each driver implements the
`meshmind.db.base_driver.GraphDriver` interface, which now accepts both namespace and entity-label filters for
`list_entities`.

## Driver Capabilities

| Driver | Module | Use Case | Notes |
| ------ | ------ | -------- | ----- |
| In-memory | `meshmind.db.in_memory_driver.InMemoryGraphDriver` | Tests and demos | Stores nodes/edges in Python dicts with UUID auto-generation helpers, plus in-process search/pagination implementations. |
| SQLite | `meshmind.db.sqlite_driver.SQLiteGraphDriver` | Lightweight persistence without external services | Uses two tables (`entities`, `triplets`) with JSON columns; supports namespace + label filtering, pagination, and SQL-based search. |
| Neo4j | `meshmind.db.neo4j_driver.Neo4jGraphDriver` | Production Bolt cluster | Requires the `neo4j` Python driver and connectivity to a running instance. Provides `verify_connectivity()` for health checks, server-side search, and aggregated counts. |
| Memgraph | `meshmind.db.memgraph_driver.MemgraphDriver` | Memgraph (Bolt-compatible) | Requires `mgclient`. Filters results using Cypher with optional namespace/label predicates, driver-side search, and count aggregation. |
| Fake drivers | `meshmind.testing.fakes` | Offline testing | Provide stubbed implementations for Redis, embedding models, and Memgraph. |

## Driver Factory

`meshmind.db.factory.graph_driver_factory` inspects `meshmind.core.config.settings.GRAPH_BACKEND` and constructs the
corresponding driver. Supported values:

- `memory`
- `sqlite`
- `neo4j`
- `memgraph`

Environment variables (see `README.md` and `ENVIRONMENT_NEEDS.md`) provide connection URIs and credentials.

## MemoryManager

`meshmind.api.memory_manager.MemoryManager` wraps driver operations and now exposes:

```python
list_memories(
    namespace: str | None = None,
    entity_labels: Sequence[str] | None = None,
    *,
    offset: int = 0,
    limit: int | None = None,
    query: str | None = None,
    use_search: bool | None = None,
) -> List[Memory]

count_memories(namespace: str | None = None) -> Dict[str, Dict[str, int]]
```

Filtering and pagination at this layer keep retrieval queries efficient when large graphs are present. The manager defers
to driver-provided `search_entities` and `count_entities` helpers when available, then handles `add_memory`,
`update_memory`, `delete_memory`, and triplet equivalents by normalizing payloads and delegating to the driver.

## Maintenance & Consolidation

Scheduled tasks in `meshmind.tasks.scheduled` use the memory manager to fetch entities before running consolidation or
expiration strategies. Because `list_memories` accepts entity labels, maintenance jobs can focus on specific entity
classes without scanning the full graph.

## Adding a New Driver

1. Subclass `GraphDriver` and implement the abstract methods, including the namespace/label-aware `list_entities`.
2. Register the driver in `meshmind/db/factory.py` under a new backend key.
3. Provide fake/test doubles if the backend cannot run inside CI.
4. Update documentation (`docs/persistence.md`, `SOT.md`, `README.md`) and add tests validating CRUD behaviours.
