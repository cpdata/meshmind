# MeshMind Project Overview

## Vision and Scope
- Transform unstructured text into graph-backed `Memory` records enriched with embeddings and metadata.
- Offer pipelines for extraction, preprocessing, storage, and retrieval that can be orchestrated from CLI tools or bespoke agents.
- Enable background maintenance workflows (expiry, consolidation, compression) once supporting services are provisioned.

## Current Architecture Snapshot
- **Client façade**: `meshmind.client.MeshMind` composes a provider-agnostic LLM client, configurable embedding model, registry
  bootstrap, and a lazily created graph driver selected via `GRAPH_BACKEND` (memory, SQLite, Memgraph, Neo4j). Retrieval helpers expose
  hybrid, vector, regex, exact, and reranked flows.
- **Pipelines**: Extraction (LLM + function calling), preprocessing (deduplicate, score, compress), and storage utilities live in
  `meshmind.pipeline`. Maintenance helpers consolidate duplicates and expire stale memories.
- **Graph layer**: `meshmind.db` defines `GraphDriver` and implements in-memory, SQLite, Memgraph, and optional Neo4j drivers
  with a shared factory for local testing and production use.
- **Retrieval helpers**: `meshmind.retrieval` now covers BM25, fuzzy, hybrid, vector-only, regex, exact-match, and LLM rerank
  workflows with shared filters, reranker utilities, and driver-side filtering/pagination to minimise Python hydration.
- **Task runners**: `meshmind.tasks` configures Celery beat to run expiry, consolidation, and compression. Drivers/managers
  initialize lazily so import-time failures are avoided.
- **Support code**: `meshmind.core` provides configuration, data models, embeddings, similarity math, and optional dependency
  guards around tokenization.
- **Service adapters**: `meshmind.api.rest` and `.grpc` expose REST/gRPC entry points (with lightweight stubs for tests) so
  ingestion and retrieval can run as services, including `/memories/counts` for namespace/label summaries.
- **Observability**: `meshmind.core.observability` collects metrics, gauges, and structured log events across pipelines and
  scheduled tasks.
- **Tooling**: The CLI ingest command (`meshmind ingest`), updated example script, Makefile automation, CI workflow, and Docker
  Compose file illustrate extraction → preprocessing → storage → retrieval locally.
- **Compatibility & fakes**: `_compat/pydantic` keeps models working when Pydantic is absent, while `meshmind/testing` provides fake Memgraph, Redis, and embedding drivers for offline test runs.

## Implemented Capabilities
- Serialize knowledge as `Memory` (nodes) and `Triplet` (relationships) Pydantic models with namespaces, metadata, embeddings,
  timezone-aware timestamps, TTL, and importance fields.
- Extract structured memories from text via the provider-agnostic `LLMClient` (Responses API compatible), with encoder registration handled during bootstrap.
- Deduplicate memories by name and cosine similarity, score importance heuristically (token diversity, recency, metadata, embedding magnitude), and compress metadata when `tiktoken` is installed.
- Persist memory nodes and triplet relationships through the storage pipeline and `MemoryManager` CRUD helpers.
- Configure LLM providers globally via `LLM_*` environment variables while supporting per-request overrides through CLI flags,
  REST/gRPC payloads, and the shared `LLMClient` wrapper.
- Perform hybrid, vector-only, regex, exact-match, fuzzy, and BM25 retrieval with optional metadata filters and LLM reranking, leveraging driver-side filtering/pagination to shrink result sets before scoring.
- Summarize stored memories by namespace/entity label via the CLI (`meshmind admin counts`) and REST `/memories/counts` route.
- Provide CRUD surfaces on `MeshMind` for creating, updating, deleting, and listing memories and triplets.
- Run Celery maintenance tasks (expiry, consolidation, compression) that tolerate missing graph drivers until runtime and persist consolidated/compressed memories back to the selected backend.
- Demonstrate ingestion, relationship creation, and retrieval in `examples/extract_preprocess_store_example.py`.
- Automate linting, formatting, type checking, and testing through the Makefile and GitHub Actions.

## Partially Implemented or Fragile Areas
- The LLM-backed embedding wrapper still assumes dictionary-style responses; adjust once SDK models are fully adopted.
- Neo4j driver support is import-guarded; the new CLI connectivity check still needs validation against a live cluster.
- Maintenance tasks rely on in-process heuristics for consolidation summaries; long-term storage and conflict resolution rules need validation.
- Importance scoring now records telemetry but still relies on heuristics; richer scoring logic or LLM-assisted ranking is pending.
- SQLite driver currently stores JSON blobs; future work may normalize columns for structured querying.

## Missing or Broken Capabilities
- Graph-backed retrieval still hydrates namespace/entity-label filtered candidates client-side; pushing ranking into the graph store is future work.
- Predicate management remains internal to the bootstrap process; external administration APIs are still missing.
- Metrics remain in-memory; external exporters (Prometheus/OpenTelemetry) are not wired up.
- gRPC wiring currently relies on stubs; production-ready servers are still future work.
- Compatibility shims provide minimal validation and should be replaced with real Pydantic models in production builds; see
  `DUMMIES.md` for a complete inventory and retirement plan.

## External Services & Dependencies
- **Graph backend**: Choose via `GRAPH_BACKEND`. In-memory and SQLite require no external services. Memgraph needs the `pymgclient` package (which exposes the `mgclient` module);
  Neo4j requires the official driver and a live instance.
- **LLM providers**: Install the OpenAI SDK (or compatible fork) for extraction, embeddings, and reranking; configure `LLM_API_KEY` (or fallback `OPENAI_API_KEY`) and the `LLM_*` model/base URL overrides as needed.
- **tiktoken**: Optional but necessary for compression/token budgeting.
- **RapidFuzz, scikit-learn, numpy**: Support fuzzy and lexical retrieval.
- **Celery + Redis**: Optional but necessary for scheduled maintenance jobs.
- **sentence-transformers**: Optional embedding backend for offline models.
- **ruff, pyright, typeguard, toml-sort, yamllint**: Development tooling invoked by the Makefile and CI workflow.

## Tooling and Operational State
- `Makefile` exposes `install`, `lint`, `fmt`, `fmt-check`, `typecheck`, `test`, `check`, `docs-guard`, `docker`, and `clean`
  targets. `make install` installs the `.[dev,docs,testing]` extras so optional dependencies are present.
- `.github/workflows/ci.yml` runs formatting/linting checks, the documentation guard, and pytest on push and pull requests.
- Tests rely on fixtures (`memory_factory`, `dummy_encoder`, in-memory drivers) and compatibility shims so they pass without external services, though installing optional dependencies improves fidelity.
- Developer-facing documentation now lives in `docs/` alongside the canonical `README.md`; the docs guard (`make docs-guard`) enforces synchronized updates when modules change.
- Docker Compose now provisions Memgraph, Neo4j, and Redis; integration-specific stacks (including the Celery worker) live under
  `meshmind/tests/docker/`. See `ENVIRONMENT_NEEDS.md` and `SETUP.md` for enabling optional services locally.

## Roadmap Highlights
- Push graph-backed retrieval deeper into the drivers (vector similarity, structured filters) so the new server-side filtering/pagination evolves into full backend-native ranking.
- Export observability metrics to external sinks (Prometheus/OpenTelemetry) and surface dashboards.
- Enhance importance scoring with data-driven heuristics or LLM evaluation.
- Validate consolidation heuristics and conflict-resolution rules against real datasets.
- Validate Neo4j driver behaviour against a live cluster and ship official test doubles for Memgraph/Redis/encoders.
- Continue refining documentation to reflect setup, troubleshooting, and architectural decisions.
- Reintroduce full Pydantic models once dependency availability is guaranteed in target environments.

## Future Potential Extensions
- Plugin-based encoder and retriever registration for runtime extensibility.
- Streaming ingestion workers (queues, webhooks) beyond batch CLI workflows.
- UI or agent-facing dashboards for curation, monitoring, and analytics.
- Automated CI pipelines for release packaging, schema migrations, and integration tests.
