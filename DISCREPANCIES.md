# README vs Implementation Discrepancies

## Overview
- The legacy README still promises a fully featured memory graph with multi-level APIs, relationship storage, and diverse
  retrieval methods. Many of those features now exist, but the document remains outdated and should be replaced by
  `README_LATEST.md`.
- The current codebase delivers extraction, preprocessing, triplet persistence, CRUD helpers, and expanded retrieval strategies
  that were missing when the README was written.
- Remaining gaps primarily involve graph-backed retrieval, observability, and automated infrastructure provisioning.

## API Surface
- ✅ `MeshMind` now exposes CRUD helpers (`create_memory`, `update_memory`, `delete_memory`, `list_memories`, triplet helpers)
  that the README referenced implicitly.
- ✅ Triplet storage routes through `store_triplets` and `MemoryManager.add_triplet`, calling `GraphDriver.upsert_edge`.
- ⚠️ The README still references `register_entity`, `register_allowed_predicates`, and `add_predicate`; predicate management is
  handled automatically but there is no public API matching those method names.
- ⚠️ README snippets showing `mesh_mind.store_memory(memory)` should be updated to call `store_memories([memory])` or the new
  CRUD helpers.

## Retrieval Capabilities
- ✅ Vector-only, regex, exact-match, hybrid, BM25, fuzzy, and optional LLM rerank searches exist in `meshmind.retrieval.search`
  and are surfaced through `MeshMind` helpers.
- ⚠️ README implies retrieval queries the graph directly. Current search helpers operate on in-memory lists supplied by the
  caller; Memgraph-backed retrieval remains future work.
- ⚠️ Named helpers like `search_facts` or `search_procedures` never existed; the README should reference the dispatcher plus
  specialized helpers now available.

## Data & Relationship Modeling
- ✅ Predicates are persisted automatically when storing triplets and tracked in `PredicateRegistry`.
- ⚠️ README examples that look up subjects/objects by name still do not match the implementation, which expects UUIDs. Add
  documentation explaining how to resolve names to UUIDs before storing edges.
- ⚠️ Consolidation and expiry remain limited to Celery jobs; README narratives about integrated maintenance still overstate the
  current persistence story.

## Configuration & Dependencies
- ✅ `README_LATEST.md` and `NEEDED_FOR_TESTING.md` document required environment variables, dependency guards, and setup steps.
- ⚠️ The legacy README omits optional tooling now required by the Makefile/CI (ruff, pyright, typeguard, toml-sort, yamllint).
- ⚠️ Python version support in `pyproject.toml` (3.13) still diverges from what many dependencies officially support; update the
  documentation or relax the requirement.

## Example Code Paths
- ✅ Updated example scripts demonstrate extraction, triplet creation, and multiple retrieval strategies.
- ⚠️ Legacy README code that instantiates custom Pydantic entities remains inaccurate; extraction returns `Memory` objects and
  validates `entity_label` names only.
- ⚠️ Search examples should be updated to show the new helper functions and optional rerank usage instead of nonexistent
  `search_facts`/`search_procedures` calls.

## Tooling & Operations
- ✅ Makefile and CI workflows now exist, aligning with README promises about automation once the README is refreshed.
- ⚠️ Docker Compose still lacks service definitions for Memgraph/Redis; README setup sections should call this out explicitly.
- ⚠️ Celery tasks remain best-effort shims; README should clarify that maintenance requires the optional infrastructure.

## Documentation State
- Promote `README_LATEST.md` as the authoritative guide, archive the legacy README, and ensure future updates propagate to
  supporting docs (`SOT.md`, `PLAN.md`, `NEEDED_FOR_TESTING.md`).
