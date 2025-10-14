# Issue Backlog

- [ ] Restore the high-level client surface promised in the README (entity/predicate registration, `add_memory`, `store_memory`, `add_triplet`).
- [ ] Persist graph relationships: extend the storage pipeline to write edges/triplets instead of only upserting nodes.
- [ ] Provide a reliable vector search entrypoint and implement regex/exact-match/LLM rerank retrieval options as documented.
- [ ] Register a default embedding encoder (e.g., OpenAI) on startup so extraction works out of the box.
- [ ] Make `MeshMind` initialization resilient when `mgclient` or Memgraph are unavailable (lazy driver creation or optional in-memory driver).
- [ ] Fix `meshmind.pipeline.compress` to handle missing `tiktoken` gracefully (skip compression or supply a fallback encoder).
- [ ] Guard `meshmind.core.utils` against importing `tiktoken` at module import time to avoid `ModuleNotFoundError`.
- [ ] Update `OpenAIEmbeddingEncoder.encode` to use the modern OpenAI SDK response objects (access `.data`, not dictionary keys) and add error handling/tests.
- [ ] Rework Celery task initialization so `MemgraphDriver` is created lazily within tasks instead of module import time side effects.
- [ ] Ensure tests are executable: remove assumptions about non-existent hooks (`Memory.pre_init`), patch the OpenAI client correctly, and supply dependency fakes.
- [ ] Align Python version and tooling guidance across `pyproject.toml`, README, and CONTRIBUTING (e.g., Python >=3.13 vs. 3.10+, missing `ruff/isort/black` dependencies).
- [ ] Document runtime dependencies explicitly (Memgraph, Redis, OpenAI API key, mgclient) and provide setup scripts or docker-compose services.
- [ ] Build relationship/query abstractions on top of `MemgraphDriver` (e.g., `get_memories`, `search` APIs) instead of expecting consumers to craft Cypher manually.
- [ ] Add integration/e2e tests covering the ingestion pipeline end-to-end with a test Memgraph instance or an in-memory driver substitute.
