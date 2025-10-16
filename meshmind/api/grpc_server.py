"""Runtime gRPC server utilities for MeshMind."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable, Sequence
from typing import Any

import grpc

from meshmind.api.grpc import GrpcServiceStub
from meshmind.api.service import MemoryService
from meshmind.protos import memory_service_pb2_grpc as pb2_grpc

__all__ = [
    "create_server",
    "serve",
    "serve_forever",
]


def create_server(
    memory_service: MemoryService,
    *,
    host: str = "0.0.0.0",
    port: int = 50051,
    interceptors: Iterable[grpc.ServerInterceptor] | None = None,
    options: Sequence[tuple[str, Any]] | None = None,
) -> tuple[grpc.aio.Server, int]:
    """Instantiate a gRPC server for the provided service.

    Returns the server instance and the bound port. Passing ``port=0`` allows the
    OS to select a free port which is reported in the return value.
    """

    server = grpc.aio.server(
        interceptors=list(interceptors or []),
        options=list(options or []),
    )
    pb2_grpc.add_MeshMindServiceServicer_to_server(GrpcServiceStub(memory_service), server)
    bound_port = server.add_insecure_port(f"{host}:{port}")
    if bound_port == 0:
        raise RuntimeError("Failed to bind MeshMind gRPC server port")
    return server, bound_port


async def serve(
    memory_service: MemoryService,
    *,
    host: str = "0.0.0.0",
    port: int = 50051,
    interceptors: Iterable[grpc.ServerInterceptor] | None = None,
    options: Sequence[tuple[str, Any]] | None = None,
    shutdown_grace: float = 5.0,
    startup_event: asyncio.Event | None = None,
) -> None:
    """Run the gRPC server until cancellation."""

    server, bound_port = create_server(
        memory_service,
        host=host,
        port=port,
        interceptors=interceptors,
        options=options,
    )
    await server.start()
    logging.getLogger(__name__).info(
        "MeshMind gRPC server listening on %s:%s", host, bound_port
    )
    if startup_event is not None:
        startup_event.set()
    try:
        await server.wait_for_termination()
    finally:
        await server.stop(shutdown_grace)


def serve_forever(
    memory_service: MemoryService,
    *,
    host: str = "0.0.0.0",
    port: int = 50051,
    interceptors: Iterable[grpc.ServerInterceptor] | None = None,
    options: Sequence[tuple[str, Any]] | None = None,
    shutdown_grace: float = 5.0,
) -> None:
    """Start the asynchronous server and block the current thread."""

    asyncio.run(
        serve(
            memory_service,
            host=host,
            port=port,
            interceptors=interceptors,
            options=options,
            shutdown_grace=shutdown_grace,
        )
    )
