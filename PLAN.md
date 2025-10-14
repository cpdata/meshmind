# Next Steps Plan

## Phase 1 – Stabilize the Existing Surface
1. **Adopt `NEW_README.md`** as the public README and archive the legacy version so expectations match reality.
2. **Fix critical dependency traps**:
   - Wrap `tiktoken` imports in `core/utils.py` and `pipeline/compress.py` with guards.
   - Update `OpenAIEmbeddingEncoder` to use `.data` from the modern SDK and add tests.
   - Lazily instantiate `MemgraphDriver` (e.g., in `store_memories` or via a factory) to avoid hard crashes when mgclient is missing.
3. **Auto-register embeddings**: when MeshMind starts, register an `OpenAIEmbeddingEncoder` using `settings.EMBEDDING_MODEL` so extraction works immediately.
4. **Repair the test suite**: modernize mocks for the OpenAI client, remove references to `Memory.pre_init`, and add coverage for the dependency fallbacks above.

## Phase 2 – Deliver Promised Graph Features
5. **Implement entity/predicate registration APIs** on `MeshMind`, backed by `meshmind.models.registry`. Persist this metadata in Memgraph or an internal registry.
6. **Add triplet storage**: extend the pipeline to transform memory metadata into node/edge upserts (subject–predicate–object) and expose `add_triplet` / `add_memory` helpers.
7. **Provide graph retrieval helpers**: implement functions to fetch memories by namespace, list predicates, and query neighbors directly via the driver.

## Phase 3 – Enhance Retrieval & Automation
8. **Expand retrieval modes**: add vector-only search, regex/exact match filters, and an optional LLM reranker stage configurable through `SearchConfig`.
9. **Integrate retrieval with storage**: allow `MemoryManager` or the driver to return ranked results instead of requiring callers to preload all memories.
10. **Strengthen maintenance workflows**: initialize Celery tasks lazily with logging, ensure expiry/consolidation/compression can operate when Memgraph is down (e.g., retry/backoff).

## Phase 4 – Developer Experience & Observability
11. **Align tooling**: reconcile Python version requirements, add dev dependencies (`ruff`, `isort`, `black`) to a `dev` extra, and wire CI to run lint/tests.
12. **Document architecture**: keep `SOT.md` updated, add diagrams or sequence charts, and document configuration/operations in the README.
13. **Add logging and metrics**: instrument CLI ingestion, pipeline stages, and graph operations for debugging and future monitoring.

Revisit this plan after Phase 1 to adjust scope based on effort estimates and stakeholder priorities.
