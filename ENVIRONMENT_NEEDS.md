# Tasks for Human Project Manager

- Install Python packages required for full optional coverage:
  - `neo4j` (official Bolt driver).
  - `mgclient` (Memgraph driver).
  - `redis` and `redis-py` client library for caching tasks.
  - `celery` for scheduled/async maintenance workers.
  - `tiktoken` to enable compression utilities.
  - `sentence-transformers` (future) for richer embedding heuristics.
  - `python-dotenv` (optional) to load `.env` files automatically.
- Provide system-level dependencies for the above packages (e.g., `libssl`, `libpq`, development headers) as needed by
  `mgclient` and `neo4j`.
- Provision external services and credentials:
  - Neo4j instance reachable from the execution environment with `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`.
  - Memgraph instance with `MEMGRAPH_URI`, `MEMGRAPH_USERNAME`, `MEMGRAPH_PASSWORD`.
  - Redis instance with `REDIS_URL`.
  - OpenAI API key (`OPENAI_API_KEY`) and, optionally, Azure OpenAI equivalents (future) for production-scale testing.
- Supply datasets/fixtures (future) representing large knowledge graphs to stress-test consolidation heuristics and
  driver-level filtering.
- Enable Docker or container runtime access (future) to spin up integration stacks via `docker-compose.yml`.
- Document credential management procedures and rotation cadence so secrets stay current.
