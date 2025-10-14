# MeshMind Project Overview

## Vision and Scope
- Transform unstructured text into graph-backed `Memory` records enriched with embeddings and metadata.
- Offer pipelines for extraction, preprocessing, storage, and retrieval that can be orchestrated from CLI tools or bespoke agents.
- Enable background maintenance workflows (expiry, consolidation, compression) once supporting services are provisioned.

## Current Architecture Snapshot
- **Client façade**: `meshmind.client.MeshMind` composes the OpenAI client, configurable embedding model, registry bootstrap,
  and a lazily created graph driver selected via `GRAPH_BACKEND` (memory, SQLite, Memgraph, Neo4j). Retrieval helpers expose
  hybrid, vector, regex, exact, and reranked flows.
- **Pipelines**: Extraction (LLM + function calling), preprocessing (deduplicate, score, compress), and storage utilities live in
  `meshmind.pipeline`. Maintenance helpers consolidate duplicates and expire stale memories.
- **Graph layer**: `meshmind.db` defines `GraphDriver` and implements in-memory, SQLite, Memgraph, and optional Neo4j drivers
  with a shared factory for local testing and production use.
- **Retrieval helpers**: `meshmind.retrieval` now covers BM25, fuzzy, hybrid, vector-only, regex, exact-match, and LLM rerank
  workflows with shared filters and reranker utilities.
- **Task runners**: `meshmind.tasks` configures Celery beat to run expiry, consolidation, and compression. Drivers/managers
  initialize lazily so import-time failures are avoided.
- **Support code**: `meshmind.core` provides configuration, data models, embeddings, similarity math, and optional dependency
  guards around tokenization.
- **Service adapters**: `meshmind.api.rest` and `.grpc` expose REST/gRPC entry points (with lightweight stubs for tests) so
  ingestion and retrieval can run as services.
- **Observability**: `meshmind.core.observability` collects metrics, gauges, and structured log events across pipelines and
  scheduled tasks.
- **Tooling**: The CLI ingest command (`meshmind ingest`), updated example script, Makefile automation, CI workflow, and Docker
  Compose file illustrate extraction → preprocessing → storage → retrieval locally.

## Implemented Capabilities
- Serialize knowledge as `Memory` (nodes) and `Triplet` (relationships) Pydantic models with namespaces, metadata, embeddings,
  timestamps, TTL, and importance fields.
- Extract structured memories from text via the OpenAI Responses API, with encoder registration handled during bootstrap.
- Deduplicate memories by name and cosine similarity, normalize importance, and compress metadata when `tiktoken` is installed.
- Persist memory nodes and triplet relationships through the storage pipeline and `MemoryManager` CRUD helpers.
- Perform hybrid, vector-only, regex, exact-match, fuzzy, and BM25 retrieval with optional metadata filters and LLM reranking.
- Provide CRUD surfaces on `MeshMind` for creating, updating, deleting, and listing memories and triplets.
- Run Celery maintenance tasks (expiry, consolidation, compression) that tolerate missing graph drivers until runtime.
- Demonstrate ingestion, relationship creation, and retrieval in `examples/extract_preprocess_store_example.py`.
- Automate linting, formatting, type checking, and testing through the Makefile and GitHub Actions.

## Partially Implemented or Fragile Areas
- The OpenAI embedding wrapper still assumes dictionary-style responses; adjust once SDK models are fully adopted.
- Neo4j driver support is import-guarded; automated verification against a live cluster is still pending.
- Maintenance tasks compute consolidation results in-process and do not yet write back optimized memories.
- Importance scoring remains heuristic; richer scoring logic or LLM-assisted ranking is still pending.
- SQLite driver currently stores JSON blobs; future work may normalize columns for structured querying.
- The declared Python 3.13 requirement may exceed what optional dependencies officially support.

## Missing or Broken Capabilities
- Retrieval still operates on caller-provided memory lists; direct graph queries for retrieval are not implemented.
- No public API exposes predicate registration beyond automatic registry bootstrap.
- Retrieval still operates on caller-provided memory lists; direct graph queries for retrieval are not implemented.
- No public API exposes predicate registration beyond automatic registry bootstrap.
- Metrics remain in-memory; external exporters (Prometheus/OpenTelemetry) are not wired up.
- gRPC wiring currently relies on stubs; production-ready servers are still future work.

## External Services & Dependencies
- **Graph backend**: Choose via `GRAPH_BACKEND`. In-memory and SQLite require no external services. Memgraph needs `pymgclient`;
  Neo4j requires the official driver and a live instance.
- **OpenAI SDK**: Required for extraction, embeddings, and LLM reranking; configure `OPENAI_API_KEY`.
- **tiktoken**: Optional but necessary for compression/token budgeting.
- **RapidFuzz, scikit-learn, numpy**: Support fuzzy and lexical retrieval.
- **Celery + Redis**: Optional but necessary for scheduled maintenance jobs.
- **sentence-transformers**: Optional embedding backend for offline models.
- **ruff, pyright, typeguard, toml-sort, yamllint**: Development tooling invoked by the Makefile and CI workflow.

## Tooling and Operational State
- `Makefile` exposes `lint`, `fmt`, `fmt-check`, `typecheck`, `test`, `check`, `docker`, and `clean` targets.
- `.github/workflows/ci.yml` runs formatting/linting checks and pytest on push and pull requests.
- Tests rely on fixtures (`memory_factory`, `dummy_encoder`, in-memory drivers) so they pass without external services, though
  optional dependencies may still need installation.
- Docker Compose now provisions Memgraph, Redis, and a Celery worker; see `NEEDED_FOR_TESTING.md` for enabling optional
  services locally.

## Roadmap Highlights
- Implement graph-backed retrieval queries (vector similarity, structured filters) instead of memory list inputs.
- Export observability metrics to external sinks (Prometheus/OpenTelemetry) and surface dashboards.
- Enhance importance scoring with data-driven heuristics or LLM evaluation.
- Harden Celery tasks to persist consolidation output and surface failures clearly.
- Validate Neo4j driver behaviour against a live cluster and ship official test doubles for Memgraph/Redis/encoders.
- Continue refining documentation to reflect setup, troubleshooting, and architectural decisions.

## Future Potential Extensions
- Plugin-based encoder and retriever registration for runtime extensibility.
- Streaming ingestion workers (queues, webhooks) beyond batch CLI workflows.
- UI or agent-facing dashboards for curation, monitoring, and analytics.
- Automated CI pipelines for release packaging, schema migrations, and integration tests.
