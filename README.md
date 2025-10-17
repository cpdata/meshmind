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
- ✅ Docker Compose provisions Memgraph, Neo4j, and Redis for local orchestration, with
  integration-specific stacks under `meshmind/tests/docker/` for Celery workers.
- ✅ Built-in observability surfaces structured events and in-memory metrics for pipelines and scheduled tasks while Celery consolidation/compression flows now persist their updates.
- ✅ Native Pydantic 2.x models and fake drivers let the suite run without scikit-learn, rapidfuzz, Redis, or live Memgraph instances.
- ✅ Graph-backed retrieval wrappers load memories directly from the configured driver when collections are omitted.
- ✅ Graph drivers filter by namespace and entity label before hydrating candidates, keeping hybrid searches efficient on large graphs.

## Requirements
- Python 3.11 or 3.12 recommended (`pyproject.toml` pins `>=3.11,<3.13` while third-party packages catch up).
- Configurable graph backend via `GRAPH_BACKEND` (`memory`, `sqlite`, `memgraph`, `neo4j`).
- Memgraph instance reachable via Bolt and the `pymgclient` Python package (which exposes the `mgclient` module for
  `GRAPH_BACKEND=memgraph`).
- Optional Neo4j instance with the official Python driver (when `GRAPH_BACKEND=neo4j`).
- OpenAI-compatible API key (set `LLM_API_KEY` or `OPENAI_API_KEY`) for extraction, embeddings, and optional reranking.
- Optional: Redis and Celery for scheduled maintenance tasks.
- Optional: `numpy`, `scikit-learn`, and `rapidfuzz` improve similarity and lexical matching but pure-Python fallbacks are bundled.
- Install project dependencies with `pip install -e .[dev,docs,testing]`; see `SETUP.md` for a detailed walkthrough.

## Installation
> **Tip:** For automated provisioning with internet access, run `./run/install_setup.sh` from the project root (requires sudo).

1. Create and activate a virtual environment using Python 3.11/3.12 (e.g., `uv venv`, `python -m venv .venv`).
2. Upgrade tooling and install MeshMind with all optional extras via `uv` (which
   honours the generated `uv.lock`):
   ```bash
   python -m pip install --upgrade pip
   pip install uv
   uv python pin 3.12           # keeps `.python-version` aligned with the project requirement
   uv sync --all-extras         # creates .venv and installs the dev/docs/testing extras
   ```
3. Export required environment variables (or populate `.env`; see `SETUP.md`):
   ```bash
   export OPENAI_API_KEY=sk-...
   export LLM_API_KEY=${LLM_API_KEY:-$OPENAI_API_KEY}
   export LLM_DEFAULT_MODEL=gpt-5-nano
   export LLM_DEFAULT_BASE_URL=https://api.openai.com/v1
   export LLM_EXTRACTION_MODEL=gpt-5-nano
   export LLM_EXTRACTION_BASE_URL=
   export LLM_EMBEDDING_MODEL=text-embedding-3-small
   export LLM_EMBEDDING_BASE_URL=
   export LLM_RERANK_MODEL=gpt-5-nano
   export LLM_RERANK_BASE_URL=
   export GRAPH_BACKEND=memory  # or memgraph/sqlite/neo4j
   export MEMGRAPH_URI=bolt://localhost:7687
   export MEMGRAPH_USERNAME=  # optional; Memgraph defaults to anonymous auth
   export MEMGRAPH_PASSWORD=
   export SQLITE_PATH=/tmp/meshmind.db
   export NEO4J_URI=bolt://localhost:7688
   export NEO4J_USERNAME=neo4j
   export NEO4J_PASSWORD=meshminD123
   export REDIS_URL=redis://localhost:6379/0
   export MAINTENANCE_MAX_ATTEMPTS=3
   export MAINTENANCE_BASE_DELAY_SECONDS=1.0
   export EMBEDDING_MODEL=${LLM_EMBEDDING_MODEL}
   ```

4. Provision Redis, Memgraph, and Neo4j with Docker Compose when you need external
   services:
   ```bash
   docker compose up -d
   ```
   Alternate topologies live in `meshmind/tests/docker/`; see `SETUP.md` for guidance on
   targeted stacks and teardown commands.

## Encoder Registration
`MeshMind` bootstraps encoders and entities during initialization, but custom scripts can register additional encoders:
```python
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder

if not EncoderRegistry.is_registered("text-embedding-3-small"):
    EncoderRegistry.register("text-embedding-3-small", OpenAIEmbeddingEncoder("text-embedding-3-small"))
```
You may register deterministic or local encoders (e.g., sentence-transformers) for offline testing. The
`OpenAIEmbeddingEncoder` now delegates to the provider-agnostic `meshmind.llm_client.LLMClient`, so any
OpenAI-compatible endpoint can serve embeddings once configured via environment variables or CLI overrides.

## Quick Start
```python
from meshmind.client import MeshMind
from meshmind.core.types import Memory, Triplet

mm = MeshMind()  # Uses LLM defaults from LLM_* environment variables
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
active graph backend configured through `GRAPH_BACKEND` or the driver supplied to `MeshMind`. Driver-backed searches now use
server-side filtering (`query`, `entity_labels`) and pagination (`offset`, `limit`) before in-memory scoring to avoid loading
entire namespaces.
```python
from meshmind.core.types import SearchConfig

memories = mm.list_memories(namespace="demo", entity_labels=["Knowledge"], limit=25)
config = SearchConfig(encoder=mm.embedding_model, top_k=5, rerank_model="gpt-5-nano")

hybrid = mm.search("Python", namespace="demo", entity_labels=["Knowledge"], config=config, use_llm_rerank=True)
vector_only = mm.search_vector("programming", namespace="demo", entity_labels=["Knowledge"])
regex_hits = mm.search_regex(r"Guido", namespace="demo", entity_labels=["Knowledge"])
exact_hits = mm.search_exact("Python", namespace="demo", entity_labels=["Knowledge"])
```
The in-memory and graph-backed search helpers support namespace/entity filters and optional reranking via the
provider-agnostic `LLMClient`. Entity-label filters are applied at the driver, avoiding unnecessary hydration when graphs
contain heterogeneous nodes. You can still pass explicit lists (e.g., during testing) to bypass graph access when desired.

## Command-Line Operations
```bash
meshmind ingest \
  --namespace demo \
  --instructions "Extract key facts as Memory objects." \
  ./path/to/text/files
```
The CLI bootstraps encoders/entities automatically. Ensure environment variables are set and Memgraph is reachable.
LLM connectivity is configurable per operation:

- `--llm-api-key` and `--llm-base-url` override the provider credentials for the entire run.
- `--extraction-model` / `--extraction-endpoint` adjust the Responses API call that performs entity extraction.
- `--embedding-model` / `--embedding-endpoint` override encoder generation (defaults to `LLM_EMBEDDING_MODEL`).
- `--rerank-model` / `--rerank-endpoint` control reranking when `use_llm_rerank=True` is provided to `MeshMind.search`.

### LLM Override Precedence

The `meshmind.llm_client.LLMClient` merges configuration from multiple sources before issuing
Requests API/Embeddings calls. The precedence order is:

1. **Explicit payload overrides** – REST/gRPC requests may include `llm_models`, `llm_base_urls`, and `llm_api_key`
   dictionaries; CLI commands surface equivalent `--extraction-*`, `--embedding-*`, and `--rerank-*` flags. These values
   apply to the single request being processed.
2. **Environment variables** – `LLM_*` variables (and the legacy `OPENAI_API_KEY`) define the default provider, model, and
   endpoint when no per-request overrides are supplied.
3. **Built-in defaults** – The client falls back to `gpt-5-nano` for Responses calls and `text-embedding-3-small` for
   embeddings when neither payload nor environment values exist.

This layering allows operators to set safe defaults globally while giving automation and human workflows the ability to
experiment with alternative providers on demand.

Administrative helpers expose predicate registry and telemetry insight:
```bash
meshmind admin predicates --list
meshmind admin predicates --add RELATED_TO
meshmind admin maintenance --max-attempts 5 --base-delay 2.5 --run consolidate
meshmind admin graph --backend neo4j
meshmind admin counts --namespace demo
meshmind serve-grpc --host 0.0.0.0 --port 50051 --backend memgraph
```

## Maintenance Tasks
Celery tasks in `meshmind.tasks.scheduled` provide expiry, consolidation, and compression maintenance with persistence.
```bash
celery -A meshmind.tasks.celery_app.app worker -B
```
Tasks instantiate the driver lazily, emit structured logs/metrics, and persist consolidated or compressed memories back to the selected graph driver. Consolidation writes now honour exponential backoff and retry semantics driven by `MAINTENANCE_MAX_ATTEMPTS` and `MAINTENANCE_BASE_DELAY_SECONDS`, logging every conflict and recording telemetry about retry durations. You can override those values before triggering Celery or the on-demand CLI by supplying `meshmind admin maintenance --max-attempts ... --base-delay ... --run <task>`. Provide valid environment variables and ensure Memgraph/Redis are running when using external backends.

## Tooling
- **Makefile** – `make fmt`, `make lint`, `make typecheck`, `make test`, `make check`, `make docker`, `make clean`,
  `make docs-guard`.
- **CI** – `.github/workflows/ci.yml` runs formatting checks (ruff, toml-sort, yamllint), pytest, and the documentation guard
  to ensure code changes keep the wiki up to date.
- **Examples** – `examples/extract_preprocess_store_example.py` demonstrates ingestion, triplet creation, and multiple retrieval
  strategies.
- **Dockerfile / docker-compose** – Container definition and orchestration files that provision Memgraph, Neo4j, Redis, the
  Celery worker, and the gRPC server documented in `SETUP.md` and `meshmind/tests/docker/`.
- **Provisioning scripts** – `run/install_setup.sh` and `run/maintenance_setup.sh` validate that optional packages (`fastapi`,
  `neo4j`, `pymgclient`, `uvicorn`) are present and respect `MESH_SKIP_SYSTEM_PACKAGES=1` / `MESH_SKIP_PYTHON_SYNC=1` when you
  need a dry run without network access.

## Benchmarking & Evaluation
- **Synthetic dataset generation** – `scripts/generate_synthetic_dataset.py` creates large JSONL/CSV corpora of
  memories/triplets (defaults: 10k memories, 20k triplets, 384-dim embeddings) so you can stress retrieval, consolidation,
  and integration flows before ingesting real data.
- **Synthetic dataset ingestion** – Follow the workflow documented in `docs/retrieval.md` to load the generated JSONL/CSV
  payloads into MeshMind via the Python client. The operations guide walks through batching tips and post-ingestion
  verification so benchmark runs start from a consistent baseline.
- **Importance scoring** – `scripts/evaluate_importance.py` runs the heuristic against JSON or synthetic datasets and reports
  descriptive statistics for quick regression checks.
- **Consolidation throughput** – `scripts/consolidation_benchmark.py` generates synthetic workloads to measure batch merging
  duration, skipped groups, and retry behaviour across configuration options.
- **Driver pagination** – `scripts/benchmark_pagination.py` seeds synthetic memories into the selected backend and records
  list latency by page size so operators can tune defaults before production rollouts.
  Use `make benchmarks` to run all three scripts with synthetic defaults and capture JSON summaries under `build/benchmarks/`.

## Service Interfaces
- **REST** – `meshmind.api.rest.create_app` returns a FastAPI app that exposes `/memories`, `/triplets`,
  `/search`, and `/memories/counts` endpoints. Search payloads accept:
  - `use_llm_rerank` to toggle LLM-based reranking,
  - `llm_models`, `llm_base_urls`, and `llm_api_key` dictionaries for per-request overrides,
  - `rerank_model` when you need to pin the reranker explicitly.
  Example:
-  ```json
  {
    "query": "architecture",
    "namespace": "demo",
    "entity_labels": ["Memory"],
    "top_k": 5,
    "use_llm_rerank": true,
    "llm_models": {"rerank": "openrouter/reranker-v1"},
    "llm_base_urls": {"rerank": "https://openrouter.ai/api/v1"}
  }
  ```
  Equivalent `curl` invocations against a local FastAPI instance:
  ```bash
  curl -s -X POST http://localhost:8000/search \
    -H "Content-Type: application/json" \
    -d '{"query":"architecture","namespace":"demo","entity_labels":["Memory"],"top_k":5}'
  curl -s "http://localhost:8000/memories/counts?namespace=demo"
  ```
- **gRPC** – `meshmind/protos/memory_service.proto` defines the canonical schema and generates the Python modules consumed by
  `meshmind.api.grpc.GrpcServiceStub` and the runtime helpers in `meshmind.api.grpc_server`. Call
  `meshmind.api.grpc_server.serve_forever(memory_service, host="0.0.0.0", port=50051)` to launch a production server (for
  example, wire the helper into a `uvicorn`-style entry point after constructing a `MemoryService`). The generated
  `SearchPayload` message carries the same LLM override fields as the REST payload. To exercise a running gRPC server, use:
  ```bash
  grpcurl -plaintext -d '{"namespace":"demo"}' localhost:50051 meshmind.api.MemoryService/MemoryCounts
  ```
- **CLI** – `meshmind admin counts` proxies the new driver aggregation helper so operators can audit namespace/entity totals.
  Automated smoke tests cover the REST `/memories/counts` route and the CLI command using the in-memory driver, ensuring
  documentation snippets stay aligned with the live interface.

## Developer Documentation
- `docs/overview.md` – high-level module map.
- `docs/persistence.md` – graph driver behaviours and configuration.
- `docs/retrieval.md` – search strategies and entity-label filtering semantics.
- `docs/pipelines.md` – ingestion lifecycle.
- `docs/api.md` – REST/gRPC payloads and CLI expectations.
- `docs/testing.md` – pytest layout and fake drivers.
- `docs/configuration.md` – environment variables and defaults.
- `docs/operations.md` & `docs/telemetry.md` – operational workflows and observability guidance.
- `docs/development.md` – contribution workflow and coding standards.
- `DUMMIES.md` – inventory of temporary shims, fakes, and compatibility layers to retire now that full dependencies are
  available.

## Observability
- `meshmind.core.observability.telemetry` collects counters, gauges, and durations for pipelines and Celery tasks.
- `meshmind.core.observability.log_event` emits structured log messages that annotate pipeline progress.
- Metrics remain in-memory today; export hooks (Prometheus, OpenTelemetry) are future enhancements.

## Test Doubles & Offline Helpers
- MeshMind now depends on first-party Pydantic 2.x models; the legacy compatibility shim has been removed.
- `meshmind/retrieval/bm25.py`, `meshmind/retrieval/fuzzy.py`, and `meshmind/core/similarity.py` include pure-Python fallbacks for scikit-learn, rapidfuzz, and numpy.
- `meshmind/testing` exports fake Memgraph, Redis, and embedding drivers that power the pytest suite and examples without external infrastructure.
- `DUMMIES.md` lists every remaining stub (for example the gRPC in-process adapter
  and offline test doubles) with guidance on whether to remove or preserve them
  once external services are provisioned.

## Testing
- Run `pytest` to execute the default suite; tests rely on fixtures and fake drivers so they do not require external services or optional libraries.
- Integration coverage lives under `meshmind/tests/test_integration_live.py` and is marked with `@pytest.mark.integration`.
  Start the docker-compose stack (`docker compose up -d`) and run `pytest -m integration` to exercise live Memgraph, Neo4j, and Redis instances.
- `make typecheck` invokes `pyright` and `typeguard`; install the tooling listed above beforehand.
- See `ENVIRONMENT_NEEDS.md` for environment requirements, docker resource guidance, and troubleshooting tips.

## Known Limitations
- Graph-backed retrieval still hydrates candidates client-side (now filtered by namespace and entity label); server-side vector search remains future work.
- Metrics remain in-memory; no external exporter is wired up yet.
- Importance scoring uses heuristics and telemetry but does not yet incorporate feedback loops or LLM-assisted ranking.

## Roadmap Snapshot
Consult `PROJECT.md`, `PLAN.md`, and `RECOMMENDATIONS.md` for prioritized enhancements: graph-backed retrieval, metrics exporters, richer importance scoring, and production-ready service deployments.
