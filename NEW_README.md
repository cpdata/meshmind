# MeshMind (Current State)

MeshMind is an experimental memory toolkit that combines LLM-assisted extraction with a property-graph backend. The present implementation focuses on turning raw text into `Memory` records, applying lightweight preprocessing, and storing them through a Memgraph-compatible driver. Retrieval helpers operate on in-memory collections of `Memory` objects and support lexical, fuzzy, and hybrid scoring.

> **Note**
> The original README described a much richer API (entity/predicate registration, triplet storage, advanced retrieval). Those features are **not** implemented yet. This document reflects the functionality that exists today.

## Features

- `Memory` data model (`meshmind.core.types.Memory`) captures namespace, entity label, metadata, optional embeddings, timestamps, and TTL/importance metadata.
- `MeshMind` client (`meshmind.client.MeshMind`) wires together an OpenAI client, an embedding model name, and a Memgraph driver, exposing helpers for:
  - `extract_memories` – LLM-based extraction that validates entity labels and populates embeddings through the encoder registry.
  - `deduplicate`, `score_importance`, `compress` – preprocessing helpers.
  - `store_memories` – persists each memory by calling `GraphDriver.upsert_entity`.
- Pipeline modules under `meshmind.pipeline` implement the extraction, preprocessing, compression, expiry, consolidation, and storage steps.
- Retrieval utilities under `meshmind.retrieval` provide TF-IDF (BM25-style) search, RapidFuzz fuzzy matching, metadata/namespace/entity-label filters, and a hybrid scorer that blends cosine similarity with lexical scores.
- `meshmind.api.memory_manager.MemoryManager` offers CRUD-style helpers over an injected graph driver (add/update/delete/list).
- `meshmind.tasks.scheduled` defines Celery tasks (optional) that invoke expiry, consolidation, and compression routines on a schedule.
- A CLI entry point (`python -m meshmind` or `meshmind` after installation) exposes an `ingest` subcommand for end-to-end extraction from local files/directories.

## Requirements

- Python 3.10+ (the package metadata currently targets 3.13; align your environment accordingly).
- A running [Memgraph](https://memgraph.com/) instance accessible via Bolt, plus the `mgclient` Python driver.
- An OpenAI API key for both extraction and embedding (set `OPENAI_API_KEY`).
- Optional services: Redis (if Celery tasks are used).
- Python dependencies listed in `pyproject.toml` (`openai`, `pydantic`, `rapidfuzz`, `scikit-learn`, `numpy`, `celery[redis]`, `sentence-transformers`, `tiktoken`, `pymgclient`, etc.).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Ensure Memgraph is running and environment variables are set:

```bash
export OPENAI_API_KEY=...  # required by openai.OpenAI()
export MEMGRAPH_URI=bolt://localhost:7687
export MEMGRAPH_USERNAME=...
export MEMGRAPH_PASSWORD=...
```

Before calling extraction, register an embedding encoder that matches `settings.EMBEDDING_MODEL` (default `text-embedding-3-small`). For example:

```python
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder
EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder())
```

## Quickstart

```python
from meshmind.client import MeshMind
from meshmind.core.types import Memory
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder

# Register the embedding encoder expected by the pipeline
EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder())

mm = MeshMind()
texts = [
    "Jane Doe is a senior software engineer based in Berlin.",
    "John Doe manages the infrastructure team in Berlin.",
]
memories = mm.extract_memories(
    instructions="Extract each distinct person as a Memory.",
    namespace="Company Directory",
    entity_types=[Memory],  # entity labels are validated against class names
    content=texts,
)
memories = mm.deduplicate(memories)
memories = mm.score_importance(memories)
memories = mm.compress(memories)
mm.store_memories(memories)
```

## Retrieval Helpers

The retrieval utilities operate on lists of `Memory` objects that are already loaded into Python (for example via `MemoryManager.list_memories`).

```python
from meshmind.retrieval.search import search, search_bm25, search_fuzzy
from meshmind.core.types import Memory, SearchConfig
from meshmind.core.embeddings import EncoderRegistry

# Register an encoder for hybrid/vector scoring
class DummyEncoder:
    def encode(self, texts):
        return [[len(t)] for t in texts]

EncoderRegistry.register("dummy", DummyEncoder())

memories = [
    Memory(namespace="Company", name="Jane Doe", entity_label="Memory", embedding=[7.0]),
    Memory(namespace="Company", name="John Doe", entity_label="Memory", embedding=[7.0]),
]
config = SearchConfig(encoder="dummy", top_k=5, hybrid_weights=(0.5, 0.5))
results = search("Jane", memories, namespace="Company", config=config)
```

## CLI Ingest

```bash
meshmind ingest \
  --namespace "Company" \
  --instructions "Extract personnel facts as Memory objects." \
  path/to/files
```

The command reads all text files, extracts memories, runs the preprocessing pipeline, and stores the results using the configured Memgraph connection.

## Maintenance Tasks (Optional)

If Celery and Redis are available, import `meshmind.tasks.scheduled` to register three periodic tasks: `expire_task`, `consolidate_task`, and `compress_task`. Each task fetches memories through `MemoryManager` and applies the corresponding pipeline helper.

## Limitations & Next Steps

- Relationship/edge storage is not implemented; only nodes are persisted.
- Custom entity models are not instantiated during extraction—only `entity_label` names are validated.
- Advanced retrieval techniques (regex search, LLM reranking, external vector databases) are not implemented yet.
- Several modules assume optional dependencies (`mgclient`, `tiktoken`, OpenAI SDK) are installed and configured.

Refer to `PROJECT.md`, `ISSUES.md`, and `PLAN.md` for the detailed roadmap.
