# Planning Thoughts

## Strategic Questions
- How aggressively should we lean into backend-native vector search versus maintaining Python-side fallbacks for portability?
- What criteria will determine when compatibility shims (Pydantic, FastAPI, FakeLLM) can be retired without regressing developer workflows?
- Which observability stack (Prometheus, OpenTelemetry Collector, custom logs) best aligns with target deployments and hosting environments?
- How do we prioritise between accuracy improvements (LLM rerank, heuristics) and operational scalability (streaming, pagination) given limited engineering capacity?

## Decision Log Candidates
- **Graph Backend Selection** – Document pros/cons of SQLite for local development versus Neo4j/Memgraph for production to guide onboarding.
- **LLM Provider Strategy** – Track evaluation results for OpenAI-compatible providers (OpenRouter, Google) and capture failover requirements.
- **Maintenance Scheduling** – Record chosen cadence, concurrency, and backoff defaults once consolidation heuristics are validated at scale.
- **Schema Governance** – Capture conventions for namespaces, entity labels, and predicate registries so ingestion pipelines stay consistent.
- **Pydantic Model Policy** – Follow the documented plan (target Pydantic 2.12+, refresh locks when 3.13 wheels land, record migration guidance) to avoid resurrecting compatibility shims.

## Upcoming Research
- Benchmark consolidation heuristics on synthetic datasets representing customer scale and capture telemetry snapshots (seed data via `scripts/generate_synthetic_dataset.py`—whose triplet CSV now includes `entity_label`—and load it using the ingestion workflow documented in `docs/retrieval.md`).
- Compare graph query latency across in-memory, SQLite, Memgraph, and Neo4j drivers when using pagination and filtering.
- Evaluate rerank quality across LLM providers using a labelled evaluation set to determine optimal default models.
- Investigate options for secure secret storage (e.g., Vault, AWS Secrets Manager) to standardise API key management.
