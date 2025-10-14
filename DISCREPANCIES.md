# README vs. Codebase Discrepancies

## API Surface
- **Missing registration APIs** – The README walkthrough relies on `MeshMind.register_entity`, `register_allowed_predicates`, `add_predicate`, `store_memory`, `add_memory`, and `add_triplet`. None of these methods exist on `meshmind.client.MeshMind`, nor do they exist elsewhere in the package.
- **No triplet storage path** – README describes storing graph triplets (node–edge–node). The shipped pipeline never touches `Triplet` and only calls `GraphDriver.upsert_entity`, so edges/predicates are never persisted.
- **Entity modelling mismatch** – README expects custom Pydantic models (e.g., `Person`) to be registered and enforced. Extraction currently hardcodes the `Memory` schema and only validates `entity_label` names against the provided classes’ `__name__`, without instantiating those models.

## Feature Claims
- **CRUD breadth** – README lists add/search/update/delete as supported capabilities. Only `meshmind.api.memory_manager.MemoryManager` exposes update/delete helpers, and they are not surfaced via the documented high-level API.
- **Retrieval methods** – README promises embedding vector search, BM25, LLM reranking, fuzzy search, exact comparison, regex search, filters, and hybrid search. The code offers BM25, fuzzy, filters, and a simple hybrid scorer; it lacks standalone vector search, regex search, exact match utilities, and any LLM-based reranking.
- **Memory preprocessing** – README references importance ranking, deduplication, consolidation, compression, and expiry. Implementations exist, but importance ranking is a fixed default of `1.0`, consolidation only keeps the highest importance duplicate, and expiry/compression are isolated Celery tasks that require additional wiring.

## Operational Expectations
- **Dependency assumptions** – README does not mention that a Memgraph instance, `mgclient`, `tiktoken`, and manual encoder registration are required. In practice, `MeshMind()` raises immediately when `mgclient` is absent, and `extract_memories` fails if the default embedding encoder is not manually registered.
- **Configuration** – README’s quickstart omits mandatory environment variables (OpenAI API key, Memgraph credentials) that `meshmind.core.config.settings` expects.
- **Testing/setup instructions** – README suggests features (e.g., graph relationships, rich retrieval) that the tests do not cover, and the declared Python requirement (`>=3.13` in `pyproject.toml`) conflicts with README/Contributing guidance (Python 3.10+).

## Example Code
- The README’s example code would fail: `MeshMind` lacks the invoked methods, extraction would reject the `Person` label unless registered (yet registration does nothing), and storing custom metadata or edges is unsupported.
- The low-level `add_triplet` example assumes the driver can create relationship edges given subject/object names; there is no such helper in the codebase, and `MemgraphDriver.upsert_edge` expects UUIDs, not arbitrary entity names.
