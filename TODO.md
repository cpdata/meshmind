# TODO

## Completed

- [x] Implement dependency guards and lazy imports for optional packages (`pymgclient`, `tiktoken`, `celery`, `sentence-transformers`).
- [x] Add bootstrap helper for default encoder registration and call it from the CLI.
- [x] Update OpenAI encoder implementation to align with latest SDK responses and retry semantics.
- [x] Improve configuration guidance and automation for environment variables and service setup.
- [x] Wire `EntityRegistry` and `PredicateRegistry` into the storage pipeline and client.
- [x] Implement CRUD and triplet methods on `MeshMind`, including relationship persistence in `GraphDriver`.
- [x] Refresh examples to cover relationship-aware ingestion and retrieval flows.
- [x] Extend retrieval module with vector-only, regex, exact-match, and optional LLM rerank search helpers.
- [x] Modernize pytest suites and add fixtures to run without external services.
- [x] Expand Makefile and add CI workflows for linting, testing, and type checks.
- [x] Document or provision local Memgraph and Redis services (e.g., via docker-compose) for onboarding.
- [x] Abstract `GraphDriver` to support alternative storage backends (Neo4j, in-memory, SQLite prototype).
- [x] Add service interfaces (REST/gRPC) for ingestion and retrieval.
- [x] Introduce observability (logging, metrics) for ingestion and maintenance pipelines.
- [x] Promote the new README, archive the legacy version, and keep SOT diagrams/maps in sync.
- [x] Harden Celery maintenance tasks to initialize drivers lazily and persist consolidation results.
- [x] Replace constant importance scoring with a heuristic driven by token diversity, recency, metadata richness, and embedding magnitude.
- [x] Create fake Memgraph, Redis, and embedding drivers for testing purposes.
- [x] Expand `GraphDriver.list_entities` to support namespace/entity-label filters and propagate the behaviour through `MemoryManager`, graph retrieval wrappers, and the MeshMind client.
- [x] Extend REST/gRPC payloads, CLI helpers, and pytest coverage to exercise the new entity-label filtering semantics.
- [x] Stand up `docs/` wiki pages, `ENVIRONMENT_NEEDS.md`, and `RESUME_NOTES.md` so documentation and session hand-off stay current.
- [x] Add unit tests covering namespace/entity-label filtering for the SQLite driver and fake drivers.
- [x] Update the example pipeline (`examples/extract_preprocess_store_example.py`) to demonstrate entity-label restricted retrieval via the MeshMind client.
- [x] Document REST/gRPC request samples that include `entity_labels` in `docs/api.md`.
- [x] Add a regression test confirming `MeshMind.list_memories` forwards `entity_labels` to the memory manager.
- [x] Push graph-backed retrieval queries deeper into Memgraph/Neo4j backends so search executes without materializing entire namespaces.
- [x] Implement pagination/streaming options in `MemoryManager.list_memories` to avoid loading entire namespaces into memory.
- [x] Add CLI/admin command to report memory counts grouped by namespace and entity label for quick health checks.
- [x] Create developer tooling (pre-commit or CI check) that ensures `docs/` pages are touched when code under corresponding modules changes.
- [x] Draft a troubleshooting section documenting optional tooling installation failures (ruff, pyright, typeguard, toml-sort, yamllint) and recommended fallbacks.
- [x] Expose `memory_counts` via the gRPC stub to keep service interfaces aligned.

- [x] Extend the docs guard mapping/tests so Docker, setup, and environment guides are enforced when related modules change.
- [x] Draft `CLEANUP.md` outlining post-restriction cleanups for files that were temporarily modified to satisfy sandbox limitations.
- [x] Audit the repository for direct `import openai` usage to scope the `llm_client` refactor.
- [x] Implement a provider-agnostic `meshmind/llm_client.py` wrapper that routes requests via configurable endpoint URLs.
- [x] Replace all direct OpenAI client interactions in the codebase with the new `llm_client` abstraction.
- [x] Update unit tests and documentation to reflect the `llm_client` usage pattern.
- [x] Extend configuration models to support per-operation LLM endpoint and model overrides with a default of `gpt-5-nano`.
- [x] Add CLI flags that override LLM endpoint/model settings when provided.
- [x] Document the cascading LLM override behaviour across README and SETUP guides.
- [x] Expose LLM override fields via REST/gRPC payloads and verify they integrate with the `llm_client` abstraction.
- [x] Add API and service-level tests covering the new LLM override payloads once implemented.
- [x] Replace `datetime.utcnow()` usage in `meshmind/_compat/pydantic.py` with timezone-aware alternatives and update any tests relying on naive timestamps.
- [x] Add a smoke test or script check that `run/install_setup.sh` and `run/maintenance_setup.sh` install key optional packages (`neo4j`, `pymgclient`, `fastapi`) when internet access is present, documenting skip behaviour when offline.
- [x] Regenerate `uv.lock` to align with the updated dependency set (`fastapi`, `uvicorn`, `neo4j`, `pymgclient`, extras) once package downloads are possible (blocked: pip cannot access PyPI from this environment).
- [x] Document per-request LLM override payloads and CLI flags across `README.md`, `docs/api.md`, and `docs/configuration.md`.
- [x] Update `SETUP.md` and `docs/operations.md` to describe the provisioning scripts' validation step and skip environment variables.
- [x] Refresh `SOT.md`, `PLAN.md`, `PROJECT.md`, and `RECOMMENDATIONS.md` to capture the LLM override workflow and timezone-aware timestamp changes.
- [x] Extend `DUMMIES.md` and `docs/testing.md` with details about `FakeLLMClient` and the new setup script smoke test.
- [x] Update `ENVIRONMENT_NEEDS.md` and `NEEDED_FOR_TESTING.md` to reflect the availability of optional packages (`fastapi`, `neo4j`, `pymgclient`, `uvicorn`).
- [x] Draft `ROADMAP.md` documenting short-, mid-, and long-term milestones extracted from the latest planning docs.
- [x] Capture architectural strategy questions in `PLANNING_THOUGHTS.md` to preserve current decision rationale.
- [x] Assemble a `research/` knowledge base summarising competitor capabilities and research references.
- [x] Implement and document maintenance retry/backoff semantics across `meshmind/tasks/scheduled.py`, configuration, and supporting docs/tests.
- [x] Add REST and CLI smoke tests covering `/memories/counts` so docs and examples stay executable with the in-memory driver.
- [x] Validate consolidation heuristics on larger datasets to confirm accuracy and stability under load.
- [x] Establish evaluation loops (analytics or LLM-assisted) to tune the new importance heuristic over time (initial synthetic benchmarking scripts in place).
- [x] Replace the compatibility shim with production Pydantic models once upstream packaging supports the target Python versions.
- [x] Verify curl/grpcurl snippets against running REST/gRPC services once infrastructure is available (FastAPI TestClient + gRPC stub coverage).
- [x] Add CLI flags for maintenance retry overrides so operators can tune `MAINTENANCE_MAX_ATTEMPTS`/`MAINTENANCE_BASE_DELAY_SECONDS` per run.
- [x] Benchmark driver-side pagination/filtering on large datasets to tune default candidate limits and document recommended overrides (synthetic benchmarks implemented).
- [x] Create a synthetic consolidation benchmark script that logs retry telemetry snapshots for analysis.
- [x] Generate protobuf definitions for the gRPC service (`meshmind/protos/memory_service.proto`) and refactor `meshmind.api.grpc` to use the canonical schema.
- [x] Update REST/gRPC documentation and tests (`README.md`, `docs/api.md`, `docs/testing.md`, `meshmind/tests/test_service_interfaces.py`, `meshmind/tests/test_api_examples.py`) to reflect the protobuf-backed interface.
- [x] Add a `make benchmarks` target that runs the synthetic benchmarking scripts and documents the workflow across README and docs.
- [x] Regenerate `uv.lock` after installing gRPC tooling and optional dependencies when network and permissions allow.

## Priority Tasks

- [ ] Validate Neo4j driver requirements and connectivity against a live cluster (exercise CLI admin checks end-to-end).
- [ ] Implement backend-native vector similarity queries for Memgraph/Neo4j to eliminate Python-side scoring when embeddings are present.
- [ ] Run `scripts/consolidation_benchmark.py` against a ≥10k-memory dataset and document recommended retry defaults in `README.md` and `ENVIRONMENT_NEEDS.md`.
- [ ] Run `scripts/benchmark_pagination.py` against live Memgraph/Neo4j instances to tune default pagination limits and capture guidance in `docs/retrieval.md`.
- [ ] Implement integration tests exercising `meshmind admin maintenance --max-attempts/--base-delay` with a real Celery worker and Redis once infrastructure is available.
- [ ] Validate the documented curl/grpcurl snippets against deployed REST/gRPC services (with auth) once staging environments are reachable.
- [ ] Implement a deployable gRPC server (using the generated protobuf modules) and add smoke tests that exercise the running service.
- [ ] Add packaging tests ensuring `meshmind/protos/memory_service.proto` is bundled and accessible via `meshmind.protos.data_path()`.
- [ ] Document operational guidance for running the gRPC server (SETUP, docs/api) once the service implementation lands.
- [ ] Add a Makefile/CI task that regenerates protobuf bindings and fails when `meshmind/protos/memory_service.proto` or the generated modules drift.

## Recommended Waiting for Approval Tasks

- [ ] Provision Neo4j, Memgraph, and Redis instances accessible from the development environment to unblock live integration tests (requires infrastructure approval).
- [ ] Approve installation of optional dependencies (`neo4j`, `pymgclient`, `redis`, `celery`, `tiktoken`, `sentence-transformers`) across CI and developer machines to exercise full workflows.
- [ ] Source or generate large synthetic datasets for consolidation and retrieval benchmarking to validate heuristics under load.
- [ ] Define a policy for reintroducing Pydantic models (version targets, rollout timeline) so compatibility shims can be retired once approved.
