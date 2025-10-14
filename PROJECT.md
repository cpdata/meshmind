# Project Overview

MeshMind is positioned as a knowledge management toolkit that combines large language models (LLMs) with a property graph store. The current codebase delivers a minimal pipeline for turning unstructured text into `Memory` records, performing lightweight preprocessing, and persisting them through a Memgraph-compatible driver. Retrieval utilities provide lexical, fuzzy, and simple hybrid (vector + lexical) ranking for in-memory collections of `Memory` objects. Supporting modules include a CLI ingest command, Celery task stubs for maintenance, and helper utilities for embeddings and similarity calculations.

## Current Capabilities

- **Memory data model** – `meshmind.core.types.Memory` defines the canonical shape of a stored memory, including namespace, entity label, metadata, embeddings, timestamps, importance score, and optional TTL. `Triplet` and `SearchConfig` models support relationship payloads and retrieval configuration.
- **Client façade** – `meshmind.client.MeshMind` wraps together an OpenAI client, an embedding model name, and a `MemgraphDriver`. It exposes helpers for extraction, deduplication, importance scoring, compression, and persistence by delegating into the pipeline modules.
- **Extraction pipeline** – `meshmind.pipeline.extract.extract_memories` orchestrates OpenAI function-calling against the `Memory` schema, enforces allowed entity labels, populates namespaces, and computes embeddings via the encoder registry.
- **Preprocessing utilities** – `meshmind.pipeline.preprocess` contains functions for deduplication (by name or embedding similarity), default importance scoring, and token-aware compression delegation. `meshmind.pipeline.compress` provides a truncation-based compressor (requires `tiktoken`).
- **Storage adapter** – `meshmind.pipeline.store.store_memories` iterates `Memory` objects and calls `GraphDriver.upsert_entity`; `meshmind.api.memory_manager.MemoryManager` provides CRUD helpers over an injected graph driver.
- **Graph driver** – `meshmind.db.memgraph_driver.MemgraphDriver` implements `GraphDriver` using `mgclient`, exposing `upsert_entity`, `upsert_edge`, `find`, `delete`, and a naïve in-memory cosine similarity search fallback.
- **Retrieval helpers** – `meshmind.retrieval` includes TF-IDF “BM25” search, RapidFuzz-based fuzzy matching, metadata/namespace/entity-label filters, and a hybrid scorer that fuses embedding cosine similarity with lexical scores (requires encoders to be registered).
- **Maintenance tasks** – `meshmind.tasks.scheduled` declares Celery beat schedules (if Celery/Redis are available) for expiry, consolidation, and compression. The tasks call the corresponding pipeline helpers through a `MemoryManager` when the Memgraph driver can initialize.
- **Command line ingest** – `meshmind.cli.__main__` exposes an `ingest` subcommand that crawls files/folders, extracts memories, preprocesses them, and stores the results.
- **Examples and tests** – `examples/extract_preprocess_store_example.py` demonstrates the manual pipeline, while `meshmind/tests` supplies pytest suites covering extraction mocking, preprocessing, retrieval, similarity, and driver behavior (many rely on monkeypatching dummy dependencies).

## Broken or Incomplete Capabilities

- The high-level client lacks the API surface described in the original README (no `register_entity`, `register_allowed_predicates`, `add_memory`, `store_memory`, or `add_triplet`).
- Relationship management is effectively missing: `store_memories` only upserts nodes, and there is no path that persists edges or triplets.
- Retrieval coverage is partial. There is no dedicated vector-search entrypoint, no regex or exact-match search, and no LLM reranking despite README claims.
- Encoder registration is entirely manual; without pre-registering an encoder name that matches `settings.EMBEDDING_MODEL`, extraction fails with `KeyError`.
- `MeshMind` initialization unconditionally requires `mgclient`; without the package or a running Memgraph instance, the client raises `ImportError` at construction time.
- `meshmind.pipeline.compress` assumes `tiktoken` is installed even after setting `tiktoken = None` on ImportError; calling `compress_memories` without the library causes an `AttributeError`.
- `meshmind.core.utils` imports `tiktoken` at module import time without guarding for missing dependencies.
- `OpenAIEmbeddingEncoder.encode` assumes OpenAI responses behave like dictionary payloads; the current OpenAI SDK returns objects with attribute access, leading to runtime errors.
- Celery tasks import and initialize `MemgraphDriver` at module scope; with `mgclient` missing, they fall back to `None`, but any later access to `manager` silently no-ops.
- Tests in `meshmind/tests` assume pytest fixtures and dummy hooks that do not exist in the production code (`Memory.pre_init`, `openai.responses.create` signatures, etc.), leaving the suite non-executable without additional scaffolding.

## Future Opportunities / Roadmap Sketch

- Restore the full high-level API promised in the README: entity registration, predicate management, triplet storage, and multi-level accessors (extract/store, add_memory, add_triplet).
- Expand graph persistence to write relationships alongside nodes, and surface query helpers for graph traversals.
- Provide first-class retrieval APIs (vector search via driver, regex/exact match filters, optional LLM rerank stage, pagination, scoring metadata).
- Harden dependency management: lazy-load optional packages, supply fallbacks or mocks, and document required services (Memgraph, Redis).
- Improve encoder ergonomics by auto-registering defaults (OpenAI embeddings) and offering local encoder options without manual setup.
- Build comprehensive integration tests that exercise real pipelines against temporary Memgraph/Redis containers (or provide in-memory substitutes).
- Update documentation to align with the implemented surface area and clearly communicate configuration, limitations, and extension points.
- Provide developer tooling parity (lint/format commands that match declared dependencies, realistic Python version constraints) and CI pipelines.
