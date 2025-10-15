# MeshMind — Plan to Exceed All Agent Memory Platforms

## Priorities (P0)
1. **MCP Server (official)**: Tools `add_memory`, `search_facts`, `search_nodes`, `get_episodes`, `delete_episode`, `clear_graph`, plus `add_triplets`, `query_triplets`, `explain_path`.
2. **Bi-temporal edges**: Adopt `valid_from/valid_to` and `tx_from/tx_to`; offer `as_of` search param & invalidation semantics.
3. **Hybrid retrieval recipes**: Implement BM25 + Embeddings + optional BFS traversal with **RRF/MMR** + **node-distance** reranking (focal entity).
4. **Multi-level scopes**: First-class `user_id`, `agent_id`, `session_id`, `run_id` across models, indexes, REST, and CLI; purge/reset by scope.
5. **Auth + tenancy by default**: API key/JWT, rate limits, tenancy checks at the driver layer; full OpenAPI with compatibility shims and contract tests.

## P1 (Scale and DX)
6. **Provider interfaces**: Add drivers for Qdrant/Chroma/Azure AI Search; embedder strategy (OpenAI/Anthropic/Ollama) with cost/latency metrics.
7. **Consolidation planner**: LLM policy for ADD/UPDATE/DELETE, contradiction detection, and audit trails; hooks for human review.
8. **OpenTelemetry**: Traces (pipelines, retrieval, LLM calls) + metrics dashboards; per-route latency and recall@k.
9. **SDKs + examples**: Ship TS & Python SDKs; notebooks and LangGraph/CrewAI integrations; Docker Compose for MCP + OTel.
10. **Admin/maintenance CLI**: Reindex, compact, prune by TTL/scope, export/import graph.

## P2 (Differentiators)
11. **Graph-aware personalization**: `focal_node_uuid` and implicit user/persona graphs to boost relevant results.
12. **Data governance**: PII scrubbing, redaction, encryption-at-rest, and retention policies per scope.
13. **Evaluation harness**: Public benchmark with Recall@k/MRR/NDCG, latency, and token cost for multiple recipes and backends.
14. **Browser ingestion**: Example Chrome extension (optionally via MCP) to capture pages/snippets with provenance into MeshMind.
