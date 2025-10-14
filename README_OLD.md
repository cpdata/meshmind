# MeshMind

MeshMind is an experimental memory orchestration service that pairs large language models with a property graph. It extracts
structured `Memory` records from unstructured text, enriches them with embeddings and metadata, and stores both nodes and
relationships via a Memgraph driver. Retrieval helpers operate on in-memory collections today, offering hybrid, vector-only,
regex, exact-match, fuzzy, and BM25 scoring with optional LLM reranking.

## Status at a Glance
- ✅ `meshmind.client.MeshMind` orchestrates extraction, preprocessing, storage, CRUD helpers, and retrieval wrappers.
- ✅ Pipelines deduplicate memories, score importance with token/recency/metadata heuristics, compress metadata, and persist nodes and triplets.
- ✅ Retrieval helpers expose hybrid, vector-only, regex, exact-match, BM25, fuzzy, and rerank workflows with namespace/entity
  filters.
- ✅ Celery tasks for expiry, consolidation, and compression initialize lazily and run when Redis and Memgraph are configured.
- ✅ Makefile and GitHub Actions provide linting, formatting, type checking, and pytest automation.
- ✅ Docker Compose provisions Memgraph, Redis, and a Celery worker for local orchestration.
- ✅ Built-in observability surfaces structured events and in-memory metrics for pipelines and scheduled tasks while Celery consolidation/compression flows now persist their updates.
- ✅ Compatibility shims and fake drivers let the suite run without Pydantic, scikit-learn, rapidfuzz, Redis, or live Memgraph instances.
- ✅ Graph-backed retrieval wrappers load memories directly from the configured driver when collections are omitted.

## Requirements
- Python 3.11 or 3.12 recommended (`pyproject.toml` pins `>=3.11,<3.13` while third-party packages catch up).
- Configurable graph backend via `GRAPH_BACKEND` (`memory`, `sqlite`, `memgraph`, `neo4j`).
- Memgraph instance reachable via Bolt and the `pymgclient` Python package (which provides the runtime `mgclient` module when
  `GRAPH_BACKEND=memgraph`).
- Optional Neo4j instance with the official Python driver (when `GRAPH_BACKEND=neo4j`).
- OpenAI API key for extraction, embeddings, and optional reranking.
- Optional: Redis and Celery for scheduled maintenance tasks.
- Optional: `numpy`, `scikit-learn`, and `rapidfuzz` improve similarity and lexical matching but pure-Python fallbacks are bundled.
- Install project dependencies with `pip install -e .`; see `pyproject.toml` for the full list.

## Installation
1. Create and activate a virtual environment using Python 3.11/3.12 (e.g., `uv venv`, `python -m venv .venv`).
2. Install MeshMind:
   ```bash
   pip install -e .
   ```
3. Install optional dependencies as needed:
   ```bash
  pip install pymgclient tiktoken sentence-transformers celery[redis] ruff pyright typeguard toml-sort yamllint
   ```
4. Export required environment variables:
   ```bash
   export OPENAI_API_KEY=sk-...
   export GRAPH_BACKEND=memory  # or memgraph/sqlite/neo4j
   export MEMGRAPH_URI=bolt://localhost:7687
   export MEMGRAPH_USERNAME=neo4j
   export MEMGRAPH_PASSWORD=secret
   export SQLITE_PATH=/tmp/meshmind.db
   export NEO4J_URI=bolt://localhost:7687
   export NEO4J_USERNAME=neo4j
   export NEO4J_PASSWORD=secret
   export REDIS_URL=redis://localhost:6379/0
   export EMBEDDING_MODEL=text-embedding-3-small
   ```

## Encoder Registration
`MeshMind` bootstraps encoders and entities during initialization, but custom scripts can register additional encoders:
```python
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder

if not EncoderRegistry.is_registered("text-embedding-3-small"):
    EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder("text-embedding-3-small"))
```
You may register deterministic or local encoders (e.g., sentence-transformers) for offline testing.

## Quick Start
```python
from meshmind.client import MeshMind
from meshmind.core.types import Memory, Triplet

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

if len(memories) >= 2:
    relation = Triplet(
        subject=str(memories[0].uuid),
        predicate="RELATED_TO",
        object=str(memories[1].uuid),
        namespace="demo",
        entity_label="Knowledge",
    )
    mm.store_triplets([relation])
```

## Retrieval
`MeshMind` exposes multiple retrieval helpers that operate on lists of `Memory` objects (e.g., fetched via
`mm.list_memories(namespace="demo")`). When you omit the `memories` argument, the client fetches candidates directly from the
active graph backend configured through `GRAPH_BACKEND` or the driver supplied to `MeshMind`.
```python
from meshmind.core.types import SearchConfig

memories = mm.list_memories(namespace="demo")
config = SearchConfig(encoder=mm.embedding_model, top_k=5, rerank_model="gpt-4o-mini")

hybrid = mm.search("Python", namespace="demo", config=config, use_llm_rerank=True)
vector_only = mm.search_vector("programming", namespace="demo")
regex_hits = mm.search_regex(r"Guido", namespace="demo")
exact_hits = mm.search_exact("Python", namespace="demo")
```
The in-memory and graph-backed search helpers support namespace/entity filters and optional reranking via the OpenAI Responses
API. You can still pass explicit lists (e.g., during testing) to bypass graph access when desired.

## Command-Line Operations
```bash
meshmind ingest \
  --namespace demo \
  --instructions "Extract key facts as Memory objects." \
  ./path/to/text/files
```
The CLI bootstraps encoders/entities automatically. Ensure environment variables are set and Memgraph is reachable.

Administrative helpers expose predicate registry and telemetry insight:
```bash
meshmind admin predicates --list
meshmind admin predicates --add RELATED_TO
meshmind admin maintenance
meshmind admin graph --backend neo4j
```

## Maintenance Tasks
Celery tasks in `meshmind.tasks.scheduled` provide expiry, consolidation, and compression maintenance with persistence.
```bash
celery -A meshmind.tasks.celery_app.app worker -B
```
Tasks instantiate the driver lazily, emit structured logs/metrics, and persist consolidated or compressed memories back to the selected graph driver. Provide valid environment variables and ensure Memgraph/Redis are running when using external backends.

## Tooling
- **Makefile** – `make fmt`, `make lint`, `make typecheck`, `make test`, `make check`, `make docker`, `make clean`.
- **CI** – `.github/workflows/ci.yml` runs formatting checks (ruff, toml-sort, yamllint) and pytest on push/PR.
- **Examples** – `examples/extract_preprocess_store_example.py` demonstrates ingestion, triplet creation, and multiple retrieval
  strategies.

## Service Interfaces
- **REST** – `meshmind.api.rest.create_app` returns a FastAPI app (or lightweight stub) that exposes `/memories`, `/triplets`,
  and `/search` endpoints.
- **gRPC** – `meshmind.api.grpc.GrpcServiceStub` mirrors the ingestion and retrieval RPC surface for integration tests and
  future server wiring.

## Observability
- `meshmind.core.observability.telemetry` collects counters, gauges, and durations for pipelines and Celery tasks.
- `meshmind.core.observability.log_event` emits structured log messages that annotate pipeline progress.
- Metrics remain in-memory today; export hooks (Prometheus, OpenTelemetry) are future enhancements.

## Compatibility & Test Doubles
- `meshmind/_compat/pydantic.py` provides a lightweight `BaseModel` implementation so the codebase functions without installing Pydantic.
- `meshmind/retrieval/bm25.py`, `meshmind/retrieval/fuzzy.py`, and `meshmind/core/similarity.py` include pure-Python fallbacks for scikit-learn, rapidfuzz, and numpy.
- `meshmind/testing` exports fake Memgraph, Redis, and embedding drivers that power the pytest suite and examples without external infrastructure.

## Testing
- Run `pytest` to execute the suite; tests rely on fixtures, fake drivers, and compatibility shims so they do not require external services or optional libraries.
- `make typecheck` invokes `pyright` and `typeguard`; install the tooling listed above beforehand.
- See `NEEDED_FOR_TESTING.md` for environment requirements and known blockers (Docker/Memgraph/Redis availability).

## Known Limitations
- Graph-backed retrieval loads namespace-scoped candidates into memory before scoring; server-side vector search remains future work.
- Metrics remain in-memory; no external exporter is wired up yet.
- Importance scoring uses heuristics and telemetry but does not yet incorporate feedback loops or LLM-assisted ranking.

## Roadmap Snapshot
Consult `PROJECT.md`, `PLAN.md`, and `RECOMMENDATIONS.md` for prioritized enhancements: graph-backed retrieval, metrics exporters, richer importance scoring, and production-ready service deployments.
