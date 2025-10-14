# Configuration Reference

MeshMind configuration is derived from environment variables and optional `.env` files (loaded when `python-dotenv` is
installed).

## Core Settings

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `GRAPH_BACKEND` | Storage backend (`memory`, `sqlite`, `neo4j`, `memgraph`). | `memory` |
| `MEMGRAPH_URI` | Bolt URI for Memgraph. | `bolt://localhost:7687` |
| `MEMGRAPH_USERNAME` / `MEMGRAPH_PASSWORD` | Credentials for Memgraph. | empty |
| `NEO4J_URI` | Bolt URI for Neo4j. | `bolt://localhost:7688` |
| `NEO4J_USERNAME` / `NEO4J_PASSWORD` | Credentials for Neo4j. | `neo4j` / `meshminD123` |
| `SQLITE_PATH` | File path for SQLite backend. | `:memory:` |
| `REDIS_URL` | Redis connection string for caching/background tasks. | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | API key for OpenAI client construction. | empty |
| `EMBEDDING_MODEL` | Default embedding model identifier. | `text-embedding-3-small` |

## Derived Behaviour

- `Settings.missing()` reports missing variables based on the selected backend (e.g., Memgraph credentials ignored when
  not using Memgraph).
- CLI commands (`meshmind.cli.__main__`) surface missing configuration early so ingestion fails fast.
- The MeshMind client reads settings during initialization to configure the default LLM client and graph driver factory.

## Recommended Secrets Management

- Store secrets in a `.env` file for local development (loaded automatically when `python-dotenv` is present).
- Use environment-specific secret managers (Vault, AWS Secrets Manager, etc.) for production deployments.
- Rotate API keys/credentials regularly and update the environment variables accordingly.

## Extending Configuration

- Add new settings to `meshmind/core/config.py` with sensible defaults.
- Update `Settings.REQUIRED_GROUPS` when additional capabilities require environment validation.
- Document the new variables here, in `README.md`, and in `ENVIRONMENT_NEEDS.md` if they require provisioning support.
