# MeshMind Overview

MeshMind is a modular framework for extracting, storing, and retrieving "memories"—structured knowledge units that
combine embeddings, metadata, and graph relationships. The platform orchestrates LLM-powered extraction pipelines,
pluggable persistence backends, and multiple retrieval strategies so applications can ingest heterogeneous content and
query it with hybrid search techniques.

## Core Concepts

- **Memories** (`meshmind.core.types.Memory`): normalized documents with embeddings, importance scores, TTLs, and
  metadata.
- **Triplets** (`meshmind.core.types.Triplet`): relationship edges connecting memories by subject/predicate/object.
- **Graph Drivers** (`meshmind.db`): persistence adapters for in-memory usage, SQLite prototyping, and Bolt-compatible
  services (Neo4j, Memgraph).
- **Pipelines** (`meshmind.pipeline`): modular stages for extraction, preprocessing, compression, and storage.
- **Retrieval** (`meshmind.retrieval`): text, vector, graph, and rerank utilities that operate on in-memory or driver-
  backed memories.
- **Service Interfaces** (`meshmind.api`): REST/gRPC-compatible surfaces and CLI tooling to automate ingestion and
  maintenance workflows.

## Project Layout

- `meshmind/core`: fundamental types, configuration, bootstrap helpers, encoders, similarity metrics, observability,
  and shared utilities.
- `meshmind/pipeline`: ingestion lifecycle components (`extract`, `preprocess`, `store`, `compress`, `consolidate`,
  `expire`).
- `meshmind/db`: graph drivers plus the factory that selects the active backend based on environment configuration.
- `meshmind/retrieval`: hybrid search primitives, graph-aware wrappers, and optional LLM rerank integration.
- `meshmind/api`: Memory service layer, REST/gRPC adapters, CLI entry points, and admin tooling.
- `meshmind/tests`: unit and integration-style tests that exercise pipelines, drivers, API stubs, and search flows
  using in-memory or fake dependencies.
- `examples/`: runnable demos showing end-to-end extraction, preprocessing, and storage pipelines.

Consult the other `docs/*.md` pages for deep dives into each subsystem.
