"""Runtime gRPC server tests."""
from __future__ import annotations

import asyncio
from contextlib import suppress

import grpc

from meshmind.api.grpc import memory_to_proto
from meshmind.api.grpc_server import create_server, serve
from meshmind.api.memory_manager import MemoryManager
from meshmind.api.service import MemoryPayload, MemoryService
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.protos import memory_service_pb2 as pb2
from meshmind.protos import memory_service_pb2_grpc as pb2_grpc
from meshmind.core.embeddings import EncoderRegistry


def test_create_server_handles_ingest_and_search() -> None:
    class _StubEncoder:
        def encode(self, texts):
            if isinstance(texts, str):
                texts = [texts]
            return [[1.0] * 3 for _ in texts]

    stub_registered = False
    if not EncoderRegistry.is_registered("text-embedding-3-small"):
        EncoderRegistry.register("text-embedding-3-small", _StubEncoder())
        stub_registered = True

    async def _run() -> None:
        driver = InMemoryGraphDriver()
        manager = MemoryManager(driver)
        service = MemoryService(manager)
        server, port = create_server(service, host="127.0.0.1", port=0)
        await server.start()
        try:
            async with grpc.aio.insecure_channel(f"127.0.0.1:{port}") as channel:
                stub = pb2_grpc.MeshMindServiceStub(channel)
                memory = MemoryPayload(
                    namespace="grpc-tests",
                    name="Alpha",
                    embedding=[0.1, 0.2, 0.3],
                )
                await stub.IngestMemories(
                    pb2.IngestMemoriesRequest(
                        memories=[memory_to_proto(memory.to_memory())]
                    )
                )
                response = await stub.Search(
                    pb2.SearchPayload(query="Alpha", namespace="grpc-tests")
                )
                assert len(response.results) == 1
                assert response.results[0].name == "Alpha"
        finally:
            await server.stop(0)

    try:
        asyncio.run(_run())
    finally:
        if stub_registered:
            EncoderRegistry._encoders.pop("text-embedding-3-small", None)


def test_serve_lifecycle_handles_cancellation() -> None:
    async def _run() -> None:
        driver = InMemoryGraphDriver()
        manager = MemoryManager(driver)
        service = MemoryService(manager)
        startup = asyncio.Event()
        task = asyncio.create_task(
            serve(service, host="127.0.0.1", port=0, startup_event=startup)
        )
        await asyncio.wait_for(startup.wait(), timeout=2.0)
        await asyncio.sleep(0.05)
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    asyncio.run(_run())
