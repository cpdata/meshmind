# MeshMind Project Overview

## Vision and Scope
- Build a practical memory service that turns unstructured text into graph-backed `Memory` records.
- Provide pipelines for extraction, preprocessing, storage, and retrieval without tightly coupling to a specific UI.
- Support background maintenance (expiry, consolidation, compression) once storage and scheduling dependencies are available.

## Current Architecture Snapshot
- **Client façade**: `meshmind.client.MeshMind` wires together an OpenAI client, a configured embedding model name, and a `MemgraphDriver` instance. Every workflow starts here.
- **Pipelines**: Extraction (LLM + function-calling), preprocessing (deduplicate, score, compress), and storage utilities live in `meshmind.pipeline`.
- **Graph layer**: `meshmind.db` exposes an abstract `GraphDriver` and a Memgraph implementation that relies on `mgclient`.
- **Retrieval helpers**: `meshmind.retrieval` operates on in-memory `Memory` lists with TF-IDF, fuzzy, and hybrid (vector + lexical) scoring.
- **Task runners**: `meshmind.tasks` defines Celery wiring for expiry, consolidation, and compression jobs when Redis and Celery are present.
- **Support code**: `meshmind.core` contains models, configuration, similarity utilities, and embedding encoder helpers. Optional dependencies (OpenAI, sentence-transformers, tiktoken) are required at runtime for many modules.
- **Tooling**: A CLI ingest command (`meshmind ingest`) demonstrates the extract → preprocess → store loop. Tests exist but depend on heavy monkeypatching and outdated SDK assumptions.

## Implemented Capabilities
- Serialize knowledge as `Memory` Pydantic models with namespace, entity label, metadata, optional embeddings, timestamps, TTL, and importance fields.
- Extract structured memories from text via the OpenAI Responses API using function-calling against the `Memory` schema (requires manual encoder registration).
- Deduplicate memories by name and (optionally) cosine similarity, assign a default importance score, and truncate metadata content using a tiktoken-based compressor.
- Persist memory nodes to Memgraph by calling `GraphDriver.upsert_entity` for each record.
- Run lexical, fuzzy, and hybrid retrieval against caller-provided in-memory lists of `Memory` objects, including optional metadata and namespace filters.
- Schedule expiry, consolidation, and compression maintenance tasks through Celery beat when both Celery and Redis are configured and the Memgraph driver initializes successfully.
- Provide an example script and CLI entry point that ingest plaintext files into a configured Memgraph instance.

## Partially Implemented or Fragile Areas
- Hybrid search depends on an encoder registered in `EncoderRegistry`; nothing is auto-registered, so out-of-the-box calls fail.
- The OpenAI embedding wrapper assumes dictionary-style responses and does not match the latest SDK payload objects.
- Celery tasks instantiate the Memgraph driver at import time; without `mgclient` they silently degrade to no-ops.
- The compressor and utility helpers import `tiktoken` eagerly and fail if the package is absent.
- Tests reference hooks (`Memory.pre_init`, OpenAI chat completions) that are no longer present, so the suite does not execute cleanly.
- Python 3.13 is declared in `pyproject.toml`, yet third-party dependencies (Celery, mgclient) have not been validated for that interpreter.

## Missing or Broken Capabilities
- No public API for registering entities, predicates, or storing triplets as promised in the legacy README.
- Graph relationships are never created because the storage pipeline only upserts nodes.
- There is no mid-level `add_memory`/`update_memory`/`delete_memory` surface on `MeshMind`; the CLI relies solely on extraction and store helpers.
- Vector search, regex search, exact match search, and LLM re-ranking endpoints described in the README are absent.
- Memory consolidation and expiry are not integrated into the ingestion workflow, and consolidation never writes results back to the database.
- Configuration guidance is minimal; missing environment variables lead to runtime failures when constructing the client.

## External Services & Dependencies
- **Memgraph + mgclient**: Required for any persistence. Without `mgclient`, constructing `MeshMind` raises immediately.
- **OpenAI SDK**: Needed for both extraction and embeddings. Newer SDK versions return typed objects, not dicts, which breaks current assumptions.
- **tiktoken**: Used by compression and token counting utilities. Imported at module load time without fallbacks.
- **RapidFuzz, scikit-learn, numpy**: Support fuzzy and lexical retrieval.
- **Celery + Redis**: Optional but necessary for scheduled maintenance tasks.
- **sentence-transformers**: Optional embedding backend for offline models.

## Tooling and Operational State
- `docker-compose.yml` lists services but does not provision Memgraph or Redis containers.
- No encoder instances are registered automatically; setup scripts are missing.
- Pytests rely on manual monkeypatches to simulate OpenAI and mgclient. Running `pytest` out of the box fails due to missing optional dependencies and incompatible SDK interfaces.
- Continuous integration or linting workflows are not defined.

## Roadmap Highlights
- Restore the high-level API surface promised in the README (entity registration, predicate management, CRUD helpers, triplet storage).
- Introduce a safe, dependency-light initialization path (lazy imports, graceful fallbacks, injectable storage backends).
- Expand retrieval to include driver-backed vector search, regex/exact match helpers, and optional LLM-based re-ranking.
- Implement relationship persistence and richer metadata handling in the graph layer.
- Harden maintenance jobs to run independently of import-time side effects and to write results back to Memgraph.
- Rewrite the test suite around modern OpenAI SDK semantics and provide fixtures for running without external services.
- Document setup thoroughly (encoders, environment variables, dependency installation, service provisioning) and provide automation scripts.

## Future Potential Extensions
- Plug-in architecture for alternative vector databases or document stores.
- Streaming ingestion workers that watch queues or webhooks instead of filesystem batches.
- UI or API gateway to expose memory search and curation to downstream agents or humans.
- Analytics dashboards that summarize namespace health, expiry cadence, and consolidation outcomes.
