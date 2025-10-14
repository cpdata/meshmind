# Service Interfaces & CLI

MeshMind exposes multiple integration points for ingestion and retrieval workflows.

## Memory Service (`meshmind.api.service`)

- `MemoryService` encapsulates ingestion (`ingest_memories`, `ingest_triplets`), search, and CRUD operations.
- `SearchPayload` accepts `entity_labels`, allowing clients to restrict search to specific entity types before hybrid
  ranking occurs.
- `MemoryPayload` and `TripletPayload` are Pydantic-compatible models shared by REST and gRPC stubs.

## REST API (`meshmind.api.rest`)

- `create_app` dynamically returns a FastAPI application if FastAPI is installed, otherwise a lightweight stub.
- Routes:
  - `POST /memories`: ingest a batch of memories.
  - `POST /triplets`: ingest relationships.
  - `POST /search`: execute hybrid search.
  - `GET /memories`: list memories (accepts `namespace` and `entity_labels`).
  - `GET /triplets`: list triplets.
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
    "namespace": "demo",
    "entity_labels": ["Memory"]
  }
  ```
- The `RestAPIStub` mirrors these routes for tests without requiring FastAPI.

## gRPC Stub (`meshmind.api.grpc`)

- Provides dataclasses representing typical RPC messages.
- `GrpcServiceStub` implements the service interface in pure Python for unit tests and demos.
- `SearchRequest` mirrors the REST payload including `entity_labels` to ensure consistent filtering semantics.

## CLI (`meshmind/cli`)

- `meshmind.cli.__main__` bootstraps default encoders, validates configuration, and exposes ingestion commands.
- `meshmind.cli.admin` contains administrative tasks for registry inspection, backend connectivity checks, and
  maintenance triggers.

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
