# Architecture

MeshMind is organized around a layered architecture that separates extraction, persistence, and retrieval concerns while
keeping the graph storage pluggable.

## High-Level Flow

1. **Extraction** (`meshmind.pipeline.extract`)
   - Uses instructions plus LLM client and embeddings to convert raw content into `Memory` objects and `Triplet`
     relationships.
2. **Preprocessing** (`meshmind.pipeline.preprocess`)
   - Deduplicates, scores importance, compresses content, and prepares payloads for persistence.
3. **Storage** (`meshmind.pipeline.store`)
   - Persists memories and triplets through the active graph driver, registering entity/predicate schemas along the way.
4. **Retrieval** (`meshmind.retrieval`)
   - Provides hybrid search, vector-only, regex, exact, fuzzy, BM25, and optional LLM rerank flows across stored
     memories.
5. **Maintenance** (`meshmind.pipeline.consolidate`, `meshmind.tasks.scheduled`)
   - Consolidates duplicates, expires stale items, and runs periodic graph hygiene tasks.

## Key Components

- **MeshMind Client (`meshmind/client.py`)**
  - High-level façade that wires pipelines, storage, and retrieval helpers. Lazily loads a graph driver via the factory
    configured by `meshmind.core.config.settings`.
  - Provides CRUD utilities, search helpers, and bootstrap logic for registries and encoders.
- **Memory Service Layer (`meshmind/api/service.py`)**
  - Encapsulates ingestion/search/triplet operations, enabling REST/gRPC adapters and CLI commands to share behaviour.
  - Applies configuration (e.g., `SearchConfig`) and now filters `list_memories` calls by namespace and entity labels to
    minimize driver loads.
- **Graph Drivers (`meshmind/db/*`)**
  - `InMemoryGraphDriver`: simple dictionaries for tests and demos.
  - `SQLiteGraphDriver`: lightweight relational persistence using JSON columns.
  - `Neo4jGraphDriver` and `MemgraphDriver`: Bolt-based implementations using Cypher.
  - All drivers implement the expanded `GraphDriver.list_entities(namespace, entity_labels)` contract for efficient
    filtering at the storage layer.
- **Observability (`meshmind/core/observability.py`)**
  - Tracks metrics, counters, and structured logs for pipeline operations.

## Data Model

Memories capture:

- `uuid`: unique identifier.
- `namespace`: logical partition to isolate tenants/workloads.
- `entity_label`: semantic label for type filtering.
- `embedding`: vector representation for similarity search.
- `metadata`: arbitrary JSON payload with content, source, annotations.
- `importance`, `ttl_seconds`, `reference_time`: scheduling and scoring hints.

Triplets connect memories with:

- `subject`, `predicate`, `object`: relationship endpoints.
- `entity_label`: stored predicate label to support filtering.
- `metadata`: additional context for the relationship.

## Extensibility

- Register new entity or predicate schemas via `EntityRegistry` and `PredicateRegistry` before persistence.
- Provide alternate graph drivers by subclassing `GraphDriver` and implementing the CRUD/search primitives.
- Extend retrieval strategies by adding new modules under `meshmind/retrieval` and wiring them through the client and
  service layers.
