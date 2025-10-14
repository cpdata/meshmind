# Additional Findings

## Dependency Handling
- `meshmind.client.MeshMind` instantiates `MemgraphDriver` on every construction. When `mgclient` is missing (default in many development environments), the import raises immediately, preventing any other functionality (including retrieval helpers) from being used.
- `meshmind.pipeline.compress` sets `tiktoken = None` when the import fails, but still calls `tiktoken.get_encoding`, raising `AttributeError`. The helper in `meshmind.pipeline.preprocess.compress` catches `ImportError`, not `AttributeError`, so the failure propagates.
- `meshmind.core.utils` imports `tiktoken` unconditionally at import time, so simply importing `meshmind.core` without the package installed triggers a crash.
- The OpenAI SDK usage is inconsistent: `meshmind.core.embeddings.OpenAIEmbeddingEncoder.encode` expects dictionary-style responses, while the modern SDK returns typed objects.

## Encoder Registry
- No encoders are registered by default. `meshmind.pipeline.extract.extract_memories` calls `EncoderRegistry.get(settings.EMBEDDING_MODEL)`; unless the caller has registered a matching encoder beforehand, the call raises `KeyError`.
- `MeshMind` does not register an encoder automatically when instantiated with the default OpenAI client, so the quickstart path fails without additional setup.

## Graph Persistence
- `meshmind.pipeline.store.store_memories` only calls `graph_driver.upsert_entity`. There is no mechanism to create edges, update predicates, or link memories. `Triplet` from `meshmind.core.types` is unused throughout the codebase.
- `meshmind.db.memgraph_driver.MemgraphDriver.upsert_edge` expects UUIDs for subject/object, but no public API surfaces those identifiers or manages the relationship lifecycle.

## Retrieval & Search
- `meshmind.retrieval.hybrid.hybrid_search` assumes that every memory already has an embedding and that an encoder is registered under `config.encoder`. It silently assigns a zero score to any memory missing an embedding, which may bury relevant results.
- There is no helper to pull memories out of Memgraph for retrieval; all search functions expect in-memory lists supplied by the caller.

## CLI & Tasks
- `meshmind.cli.ingest.ingest_command` registers `entity_types=[Memory]`. Supplying a custom Pydantic model has no effect because extraction only validates `entity_label` names; it never instantiates the provided models.
- Scheduled tasks import `MemgraphDriver` at module load and swallow any exception, leaving `manager = None`. Task invocations then return early without logging, making failures hard to diagnose.

## Testing & Tooling
- Test modules import the production code in ways that do not align with the current library versions (`openai.responses.create`, `Memory.pre_init`). Running `pytest` without heavy monkeypatching will fail.
- `pyproject.toml` pins `requires-python = ">=3.13"`, yet the documentation still references Python 3.10 and Poetry. Tooling commands in `Makefile` (ruff, isort, black) are not listed as dependencies.

## Documentation Gaps
- Runtime prerequisites (Memgraph, Redis, mgclient, encoder registration) are not described in the existing README.
- There is no architecture guide explaining how pipeline modules, the CLI, Celery tasks, and retrieval helpers relate, making it hard for new contributors to navigate the codebase.
