# README vs Implementation Discrepancies

## Overview
- The legacy README promises a fully featured memory graph service with multi-level APIs, relationship storage, and diverse retrieval methods.
- The current codebase delivers a narrower pipeline that focuses on extracting `Memory` nodes, preprocessing them, and writing them to Memgraph.
- Many examples in the README are not executable because the described methods, configuration defaults, and dependency behaviors do not exist.

## API Surface
- README shows `MeshMind.register_entity`, `register_allowed_predicates`, `add_predicate`, `store_memory`, `add_memory`, `add_triplet`, `search`, `search_facts`, `search_procedures`, `update_memory`, and `delete_memory` methods. Only `extract_memories`, `deduplicate`, `score_importance`, `compress`, and `store_memories` exist on `meshmind.client.MeshMind`.
- Entity registration is depicted as a first-class feature that validates custom Pydantic models (e.g., `Person`). The implementation merely checks that the `entity_label` returned by the LLM matches the class name; there is no registry enforcing schemas or instantiating the models.
- Triplet storage is central to the README narrative, yet the pipeline never creates edges. `MesMind` exposes no method that calls `GraphDriver.upsert_edge`, and the tests never cover triplet scenarios.
- CRUD operations (`add_memory`, `update_memory`, `delete_memory`) are discussed as mid-level helpers. Only the lower-level `MemoryManager` class (not surfaced through `MeshMind`) contains these methods.

## Retrieval Capabilities
- README advertises embedding vector search, BM25, LLM reranking, fuzzy search, exact comparison, regex search, filter support, and hybrid methods. The codebase exposes BM25, fuzzy, hybrid, and metadata filters. There are no endpoints for exact comparison, regex search, or LLM reranking, and vector search exists only as a helper inside `MemgraphDriver.vector_search` with no integration.
- The README implies that search operates against the graph database. Actual retrieval utilities work on in-memory lists provided by the caller and do not query Memgraph.
- Usage examples show three layered search calls (`search`, `search_facts`, `search_procedures`). Only the single `search` dispatcher exists, alongside `search_bm25` and `search_fuzzy` helper functions.

## Data & Relationship Modeling
- README claims memories encompass nodes and edges, including relationship predicates registered ahead of time. The code lacks predicate management beyond an unused `PredicateRegistry` and never writes relationships to the database.
- Low-level `add_triplet` examples assume subject/object lookups by name. `MemgraphDriver.upsert_edge` expects UUIDs and assumes the nodes already exist, so the documented behavior cannot work.
- Memory importance, consolidation, and expiry are presented as rich features. Implementations are minimal: importance defaults to `1.0`, consolidation simply keeps the highest-importance duplicate in-memory, and expiry only runs inside a Celery task that depends on optional infrastructure.

## Configuration & Dependencies
- README omits instructions for registering embedding encoders. In practice, `meshmind.pipeline.extract` fails with `KeyError` unless `EncoderRegistry.register` is called before extraction.
- README suggests broad Python support and effortless setup. `pyproject.toml` requires Python 3.13, yet many dependencies (Celery, mgclient) do not publish wheels for that version. Missing `mgclient` triggers an import-time failure inside `MeshMind.__init__`.
- Required environment variables (OpenAI API key, Memgraph URI/credentials, Redis URL) are not documented. The README examples instantiate `MeshMind()` with no mention of configuration, but the code depends on these settings.
- README instructs storing and searching without mentioning external services. The current implementation requires a running Memgraph instance and optional Redis for Celery beat.

## Example Code Path
- README’s extraction example instantiates `MeshMind`, registers entity classes, and expects memories to be generated with corresponding attributes. Actual extraction enforces `entity_label` only by string name and returns `Memory` objects rather than instances of the provided Pydantic models.
- The `mesh_mind.store_memory(memory)` loop in the README references a nonexistent method; the equivalent in code is `store_memories([memory])` or direct use of `MemoryManager`.
- Search examples call `mesh_mind.search`, `search_facts`, and `search_procedures`. Only `search` exists, and it requires preloaded `Memory` objects.
- Update/delete examples rely on `mesh_mind.update_memory` and `mesh_mind.delete_memory`, which are absent.

## Tooling & Operations
- README does not mention the need to register encoders before running the CLI; the default ingest command fails unless `EncoderRegistry` has an entry matching the configured embedding model.
- README implies functioning Celery maintenance processes. The Celery tasks are importable but disabled when dependencies are missing, and they do not persist consolidated results.
- README lacks troubleshooting guidance for OpenAI SDK changes. The shipped code uses response access patterns (`response['data']`) incompatible with the current SDK, leading to runtime errors.

## Documentation State
- README positions the document as the authoritative source of truth, yet large sections (triplet storage, relationship management, retrieval coverage) describe unimplemented functionality.
- The original README does not point readers to supporting documents such as configuration references, dependency requirements, or operational runbooks, leaving gaps for anyone onboarding today.
