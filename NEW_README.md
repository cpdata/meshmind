# MeshMind

MeshMind is an experimental memory orchestration service that pairs large language models with a property graph. The current code turns unstructured text into `Memory` records, applies light preprocessing, and stores them via a Memgraph driver. Retrieval helpers run in-memory using lexical, fuzzy, and hybrid scoring strategies. The project is a work in progress; many features described in the legacy README are not yet implemented.

## Status at a Glance
- ✅ High-level client (`meshmind.client.MeshMind`) with helpers for extraction, preprocessing, and storage.
- ✅ Pipelines for deduplication, default importance scoring, compression, and persistence of memory nodes.
- ✅ Retrieval helpers for TF-IDF (BM25-style), fuzzy string matching, and hybrid vector + lexical ranking (requires registered encoder).
- ✅ Celery task stubs for expiry, consolidation, and compression (require Celery + Redis + Memgraph to function).
- ⚠️ Relationship handling (triplets, predicate registration) is scaffolded but not wired into the storage pipeline.
- ⚠️ CLI ingestion requires manual encoder registration and a running Memgraph instance with `mgclient` installed.
- ❌ Mid-level CRUD APIs (`add_memory`, `update_memory`, `delete_memory`), triplet storage, regex search, and LLM reranking are not implemented.

## Requirements
- Python 3.11 or 3.12 recommended (project metadata claims 3.13 but dependency support is unverified).
- Memgraph instance reachable via Bolt and the `mgclient` Python package.
- OpenAI API key for extraction and embeddings.
- Optional but recommended: Redis and Celery for scheduled maintenance tasks.
- Additional Python packages installed via `pip install -e .` (see `pyproject.toml`). Some optional modules (`tiktoken`, `sentence-transformers`) are required for specific features.

## Installation
1. Create and activate a virtual environment using Python 3.11 or 3.12.
2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```
3. Install optional dependencies as needed:
   ```bash
   pip install mgclient tiktoken sentence-transformers redis celery
   ```
4. Export required environment variables (adapt values to your setup):
   ```bash
   export OPENAI_API_KEY=sk-...
   export MEMGRAPH_URI=bolt://localhost:7687
   export MEMGRAPH_USERNAME=neo4j
   export MEMGRAPH_PASSWORD=secret
   export REDIS_URL=redis://localhost:6379/0
   export EMBEDDING_MODEL=text-embedding-3-small
   ```

## Encoder Registration
`meshmind.pipeline.extract` expects an encoder registered in `meshmind.core.embeddings.EncoderRegistry` that matches `settings.EMBEDDING_MODEL`. Before calling extraction or the CLI, register an encoder:
```python
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder
EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder("text-embedding-3-small"))
```
For offline experimentation you may register a custom encoder that returns deterministic embeddings.

## Quick Start (Python)
```python
from meshmind.client import MeshMind
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder
from meshmind.core.types import Memory

# Register an embedding encoder once at startup
EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder())

mm = MeshMind()
texts = ["Python is a programming language created by Guido van Rossum."]
memories = mm.extract_memories(
    instructions="Extract key facts as Memory objects.",
    namespace="demo",
    entity_types=[Memory],
    content=texts,
)
memories = mm.deduplicate(memories)
memories = mm.score_importance(memories)
memories = mm.compress(memories)
mm.store_memories(memories)
```
This workflow persists `Memory` nodes in Memgraph. Relationships are not yet created automatically.

## Command-Line Ingestion
The CLI performs the same pipeline for files and folders of text documents.
```bash
meshmind ingest \
  --namespace demo \
  --instructions "Extract key facts as Memory objects." \
  ./path/to/text/files
```
Before running:
- Ensure `mgclient` can connect to Memgraph using credentials in environment variables.
- Register an embedding encoder in a startup script (e.g., run a small Python snippet prior to invocation) or extend the CLI to perform registration.
- Provide a `.env` file or export environment variables for configuration.

## Retrieval Helpers
Retrieval utilities operate on in-memory lists of `Memory` objects. Load the records from your graph (e.g., via `MemoryManager.list_memories`) before calling these helpers.
```python
from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import SearchConfig
from meshmind.db.memgraph_driver import MemgraphDriver
from meshmind.retrieval.search import search

# Load memories from Memgraph
manager = MemoryManager(MemgraphDriver("bolt://localhost:7687"))
memories = manager.list_memories(namespace="demo")

# Register the same encoder used during ingestion
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder
EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder())

config = SearchConfig(encoder="text-embedding-3-small", top_k=10)
results = search("Python", memories, namespace="demo", config=config)
for memory in results:
    print(memory.name, memory.metadata)
```
`search_bm25` and `search_fuzzy` are also available for lexical and fuzzy-only scoring. Vector search against Memgraph is not implemented; hybrid search uses embeddings stored on each memory object.

## Maintenance Tasks
`meshmind.tasks.scheduled` defines Celery beat jobs for:
- Expiring memories once `created_at + ttl_seconds` has elapsed.
- Consolidating duplicate names by keeping the highest-importance record.
- Compressing long metadata content with tiktoken.

To enable these tasks:
1. Ensure Celery and Redis are installed and running.
2. Start a Celery worker with the meshmind app:
   ```bash
   celery -A meshmind.tasks.celery_app.app worker -B
   ```
   The module attempts to instantiate `MemgraphDriver` at import time; provide valid credentials and ensure `mgclient` is available.

## Testing
- Pytests live under `meshmind/tests`. They rely on heavy monkeypatching and may need updates to align with the current OpenAI SDK.
- Some tests assume fixtures or hooks (`Memory.pre_init`) that are absent; expect failures until the suite is modernized.
- No continuous integration pipeline is currently provided.

## Known Limitations
- No triplet/relationship persistence; only nodes are stored.
- Mid-level CRUD helpers and predicate registration are missing from the public client API.
- CLI lacks ergonomics for registering encoders or custom entity models.
- Optional dependencies (`tiktoken`, `sentence-transformers`) are required at import time, leading to crashes when absent.
- The project requires significant configuration (Memgraph, Redis, OpenAI) before any end-to-end scenario succeeds.

## Roadmap Snapshot
See `PROJECT.md` and `PLAN.md` for prioritized workstreams, including restoring the documented API, improving dependency handling, and expanding retrieval coverage.
