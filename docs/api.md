# Service Interfaces & CLI

MeshMind exposes multiple integration points for ingestion and retrieval workflows.

## Memory Service (`meshmind.api.service`)

- `MemoryService` encapsulates ingestion (`ingest_memories`, `ingest_triplets`), search, and CRUD operations.
- `SearchPayload` accepts `entity_labels`, allowing clients to restrict search to specific entity types before hybrid
  ranking occurs. It also exposes `use_llm_rerank`, `llm_models`, `llm_base_urls`, `llm_api_key`, and `rerank_model` so API
  callers can override the shared `LLMClient` on a per-request basis. When these dictionaries are omitted, the service falls
  back to `LLM_*` environment variables and then the built-in defaults (`gpt-5-nano`, `text-embedding-3-small`).
- `MemoryPayload` and `TripletPayload` are Pydantic-compatible models shared by REST and gRPC stubs.

## REST API (`meshmind.api.rest`)

- `create_app` returns a FastAPI application exposing ingestion, retrieval, and
  reporting routes.
- Routes:
  - `POST /memories`: ingest a batch of memories.
  - `POST /triplets`: ingest relationships.
  - `POST /search`: execute hybrid search.
  - `GET /memories`: list memories (accepts `namespace`, `entity_labels`, `offset`, `limit`, `query`, `use_search`).
  - `GET /triplets`: list triplets.
  - `GET /memories/counts`: summarize memory counts grouped by namespace and entity label.
- Sample request bodies:
  ```json
  {
    "query": "python",
    "namespace": "demo",
    "entity_labels": ["Memory"],
    "top_k": 5,
    "encoder": "text-embedding-3-small"
  }
  ```
  ```json
  {
    "query": "architecture",
    "namespace": "demo",
    "top_k": 5,
    "use_llm_rerank": true,
    "llm_models": {"rerank": "openrouter/reranker-v1"},
    "llm_base_urls": {"rerank": "https://openrouter.ai/api/v1"}
  }
  ```
  ```json
  {
    "namespace": "demo",
    "entity_labels": ["Memory"],
    "limit": 20,
    "query": "python"
  }
  ```
  ```json
  {
    "namespace": "demo"
  }
  ```
- Example `curl` invocations against a local FastAPI server:
  ```bash
  curl -s -X POST http://localhost:8000/search \
    -H "Content-Type: application/json" \
    -d '{"query":"architecture","namespace":"demo","entity_labels":["Memory"],"top_k":5}'
  curl -s "http://localhost:8000/memories/counts?namespace=demo"
  ```

## gRPC Service (`meshmind.api.grpc` + `meshmind/api/grpc_server.py`)

- `meshmind/protos/memory_service.proto` defines the canonical MeshMind RPC schema. Use `python scripts/generate_protos.py` to
  regenerate `memory_service_pb2.py` and `memory_service_pb2_grpc.py`; CI runs `scripts/check_protos.py` to fail when the
  generated modules drift.
- `GrpcServiceStub` wires the generated protobuf messages to the `MemoryService` business logic so unit tests and demos can run
  without standing up a gRPC server.
- For production deployments, construct a `MemoryService` and call
  `meshmind.api.grpc_server.serve_forever(memory_service, host, port)` to expose the RPC interface.
- `SearchPayload` mirrors the REST payload including `entity_labels`, `use_llm_rerank`, per-operation LLM overrides, and
  rerank-specific settings. Overrides remain scoped to the single RPC and never mutate the global client configuration.
- `MemoryCountsRequest` returns namespace/entity-label aggregates so service parity with REST/CLI is preserved.
- A running gRPC server can be exercised with `grpcurl`:
  ```bash
  grpcurl -plaintext -d '{"namespace":"demo"}' localhost:50051 meshmind.api.MemoryService/MemoryCounts
  ```

## CLI (`meshmind/cli`)

- `meshmind.cli.__main__` bootstraps default encoders, validates configuration,
  and exposes ingestion commands.
- `meshmind.cli.admin` contains administrative tasks for registry inspection,
  backend connectivity checks, memory counts, and maintenance triggers. Use
  `meshmind admin maintenance --max-attempts <n> --base-delay <seconds> --run <task>`
  to override retry/backoff settings per run.
- `meshmind serve-grpc --host 0.0.0.0 --port 50051` launches the asyncio gRPC
  server defined in `meshmind.api.grpc_server` using the configured graph backend
  and LLM settings.

## Client (`meshmind/client.py`)

- `MeshMind` client wraps all pipelines and persistence methods.
- CRUD and search helpers delegate to the memory manager while respecting namespace/entity label filters.
- Search helpers automatically fetch candidates from the graph when `memories` is omitted, ensuring consistent
  behaviour across service surfaces.

## Example Workflow

1. Instantiate the client: `mm = MeshMind()` (ensure environment variables are set for your backend).
2. Ingest data using CLI (`meshmind ingest ...`) or the REST API.
3. Retrieve memories via REST (`POST /search`) or the Python client (`mm.search(...)`).
4. Monitor metrics/logs through the observability utilities (`docs/telemetry.md`).
