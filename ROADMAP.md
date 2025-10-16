# Roadmap

## Vision
- Deliver a retrieval-augmented intelligence layer that ingests heterogeneous data, consolidates knowledge, and surfaces context-aware responses through REST, gRPC, and CLI workflows.
- Support multiple graph backends (in-memory, SQLite, Memgraph, Neo4j) with consistent telemetry, maintenance, and LLM orchestration knobs.
- Provide developers with reproducible tooling, comprehensive documentation, and automation scripts that keep local and CI environments aligned.

## Near-Term (0–2 Weeks)
- Validate Neo4j and Memgraph connectivity using the new Docker Compose stacks, documenting any credential or networking gaps discovered.
- Finalize maintenance write policies by implementing retry/backoff semantics and measuring consolidation accuracy against representative datasets.
- Publish ROADMAP and PLANNING_THOUGHTS artifacts, and seed the `research/` folder with competitive analysis to ground prioritization discussions.
- Expand automated smoke tests for REST `/memories/counts`, CLI `meshmind admin counts`, and provisioning scripts to ensure guardrails stay trustworthy.
- Capture outstanding shim retirement work (Pydantic, FastAPI, FakeLLM) in CLEANUP.md with precise acceptance criteria for each removal.

## Mid-Term (2–6 Weeks)
- Run load tests against SQLite and hosted graph backends to tune pagination defaults, consolidation heuristics, and token compression strategies.
- Implement backend-native vector similarity queries and schema indexes so embeddings never leave the database during scoring.
- Finalise the gRPC surface by packaging the existing protobuf schema with a deployable server and generated clients (Python + additional languages) so external agents can integrate without the in-process stub.
- Instrument observability exports (Prometheus/OpenTelemetry) and wire dashboards/alerts for ingestion latency, queue depth, and error rates.
- Replace compatibility shims with official Pydantic/FastAPI packages once dependency constraints are lifted, and backfill validation coverage.

## Long-Term (6+ Weeks)
- Build evaluation loops—analytics dashboards and LLM-assisted reviews—that continuously score memory importance heuristics and rerank quality.
- Introduce human-in-the-loop tooling for conflict resolution, allowing operators to approve merges or override automated maintenance plans.
- Explore federated deployments that synchronise multiple MeshMind instances, including replication strategies and eventual-consistency guarantees.
- Integrate additional LLM providers (Google, Anthropic, OpenRouter) through the `llm_client` abstraction, emphasizing observability and cost controls.
- Harden security posture with RBAC, audit trails, and secrets management guidelines tailored to enterprise deployments.
