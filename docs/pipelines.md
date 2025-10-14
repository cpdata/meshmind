# Pipelines

MeshMind pipelines orchestrate the transformation of raw content into stored memories and relationships.

## Extract (`meshmind.pipeline.extract`)

- `extract_memories` uses the configured LLM client to parse unstructured content into structured `Memory` objects.
- Supports configurable entity types, instructions, and embedding models.
- Output includes candidate triplets emitted by extraction heuristics.

## Preprocess (`meshmind.pipeline.preprocess`)

- `deduplicate`: removes near-duplicate memories based on embedding cosine similarity and metadata hashes.
- `score_importance`: applies heuristic scoring that considers recency, metadata richness, token diversity, and embedding
  magnitude.
- `compress`: performs optional content compression if tiktoken is installed; otherwise acts as a no-op while recording
  telemetry.

## Store (`meshmind.pipeline.store`)

- `store_memories`: upserts each `Memory` through the graph driver after ensuring the entity type is registered.
- `store_triplets`: persists relationships while registering predicates via `PredicateRegistry`.

## Consolidate (`meshmind.pipeline.consolidate`)

- `consolidate_memories`: groups similar memories, merges metadata, and produces a plan enumerating consolidation
  outcomes for later application.

## Maintenance (`meshmind.tasks.scheduled`)

- Provides task stubs for Celery/cron that run consolidation plans, expire TTL-bound memories, and emit importance
  telemetry snapshots.

## Expiration (`meshmind.pipeline.expire`)

- Contains helpers to remove expired memories (leveraged by maintenance tasks and CLI commands).

## Usage Patterns

1. Use the MeshMind client (`MeshMind.extract_memories`) or pipeline functions directly to generate memories.
2. Preprocess the output with `deduplicate`, `score_importance`, and `compress` depending on your quality requirements.
3. Persist via `store_memories` / `store_triplets` using your configured graph backend.
4. Retrieve with hybrid or specialized searches (see `docs/retrieval.md`).
5. Schedule maintenance tasks to keep the graph clean and heuristics calibrated.
