# Cleanup Plan for Temporary Workarounds

The following actions should be executed once the development environment consistently provides internet access and all
optional dependencies can be installed. Each item references the affected files, the temporary workaround currently in
place, and the exact remediation steps required to bring the implementation in line with production expectations.

## Compatibility Layers

### Replace Pydantic Shim (Completed)
- **Files**: `meshmind/_compat/pydantic.py`, modules importing from `meshmind._compat.pydantic`.
- **Status**: Completed – the shim has been removed, `pydantic>=2.11` is a required dependency, and all models/tests now consume the official APIs directly.

### Retire FastAPI Stub
- **Files**: `meshmind/api/rest.py`, `meshmind/api/service.py`, `docs/api.md`, `SETUP.md`.
- **Current State**: A lightweight FastAPI replacement exposes REST endpoints without requiring the framework.
- **Action**:
  1. Install `fastapi`, `uvicorn`, and related extras via the setup scripts.
  2. Replace the stub implementation with a true FastAPI app using pydantic request/response models.
  3. Update tests to spin up the FastAPI test client instead of the stub.
  4. Refresh documentation to reflect the production stack only.

### Replace gRPC Dataclass Shim (Completed)
- **Files**: `meshmind/api/grpc.py`, `meshmind/protos/memory_service.proto`, `meshmind/tests/test_service_interfaces.py`, `docs/api.md`.
- **Status**: Completed – protobuf definitions now live under `meshmind/protos`, generated modules back the Python stub, setup scripts install `grpcio`/`grpcio-tools`, and tests exercise the canonical schema.

### Promote gRPC Server Implementation
- **Files**: `meshmind/api/grpc.py`, future server entry point, integration tests.
- **Current State**: Tests rely on the in-process stub; there is no deployable server or channel bootstrap yet.
- **Action**:
  1. Implement a gRPC server (synchronous or `grpc.aio`) that binds the generated service to an actual channel.
  2. Add integration tests (possibly using `grpc.aio.insecure_channel`) that cover ingestion, search, and memory counts against the running server.
  3. Document provisioning steps (`SETUP.md`, `docs/api.md`) and add CLI helpers or docker-compose services if required.

## Task Scheduling Workarounds

### Remove Celery Dummy App and Beat Fallback
- **Files**: `meshmind/tasks/celery_app.py`, `meshmind/tasks/scheduled.py`.
- **Current State**: Custom placeholders allow imports without Celery and Celery Beat.
- **Action**:
  1. Make `celery` a required dependency for maintenance tasks.
  2. Refactor scheduling utilities to import real Celery constructs and fail fast when misconfigured.
  3. Add integration tests that execute Celery workers against Redis or RabbitMQ in docker-compose.
  4. Delete fallback classes once coverage exists.

## Testing Fakes

### Evaluate Graph/Embedding/Test Fakes
- **Files**: `meshmind/testing/fakes.py`, `meshmind/tests/conftest.py`, `meshmind/tests/test_*`.
- **Current State**: In-memory drivers and dummy encoders enable offline unit tests.
- **Action**:
  1. Keep unit-test fakes for isolation but ensure parallel integration suites use live services.
  2. Document expectations in `docs/testing.md` and mark fakes clearly as test-only utilities.
  3. Remove any production code paths that accidentally import fakes.

### Replace Memgraph Client Mock
- **Files**: `meshmind/tests/test_memgraph_driver.py`.
- **Current State**: Monkeypatches a fake `mgclient` module for driver tests.
- **Action**:
  1. Install `pymgclient` and run tests against a dockerized Memgraph instance.
  2. Retain the fake only for negative/offline coverage; guard it behind an explicit fixture flag.

## Observability and Telemetry

### Confirm Logging Metrics Alignment
- **Files**: `meshmind/core/observability.py`, `meshmind/pipeline/*`, `docs/telemetry.md`.
- **Current State**: Logging/metrics rely on standard library fallbacks.
- **Action**:
  1. Integrate preferred observability stack (e.g., OpenTelemetry) once dependencies are greenlit.
  2. Remove or demote placeholders that mimic external exporters.

## Tooling and Automation

### Finalize Setup Scripts
- **Files**: `run/install_setup.sh`, `run/maintenance_setup.sh`.
- **Current State**: Scripts install packages opportunistically.
- **Action**:
  1. Review installed package list after environment unblock and remove conditional guards.
  2. Ensure scripts configure CLI tools (e.g., `grpcurl`, `neo4j-admin`) that were previously skipped offline.

### Lock Dependency Graph
- **Files**: `pyproject.toml`, `uv.lock`.
- **Current State**: Lockfile may exclude previously unavailable packages.
- **Action**:
  1. Regenerate `uv.lock` after all dependencies are installed.
  2. Commit the updated lockfile and note differences in `CHANGELOG.md`.

