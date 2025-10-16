"""REST adapters for the :mod:`meshmind` service layer."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from meshmind.api.service import MemoryPayload, MemoryService, SearchPayload, TripletPayload


class RestAPIStub:
    """Fallback handler that emulates REST routes without FastAPI."""

    def __init__(self, service: MemoryService) -> None:
        self.service = service

    def dispatch(self, method: str, path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        method = method.upper()
        payload = payload or {}
        if method == "POST" and path == "/memories":
            memories = [MemoryPayload(**item) for item in payload.get("memories", [])]
            uuids = self.service.ingest_memories(memories)
            return {"uuids": uuids}
        if method == "POST" and path == "/triplets":
            triplets = [TripletPayload(**item) for item in payload.get("triplets", [])]
            count = self.service.ingest_triplets(triplets)
            return {"stored": count}
        if method == "POST" and path == "/search":
            request = SearchPayload(**payload)
            results = self.service.search(request)
            return {"results": [mem.model_dump(exclude_none=True) for mem in results]}
        if method == "GET" and path == "/memories":
            namespace = payload.get("namespace")
            entity_labels = payload.get("entity_labels")
            offset = int(payload.get("offset", 0))
            limit_value = payload.get("limit")
            limit = int(limit_value) if limit_value is not None else None
            query = payload.get("query")
            use_search = payload.get("use_search")
            memories = self.service.list_memories(
                namespace,
                entity_labels,
                offset=offset,
                limit=limit,
                query=query,
                use_search=use_search,
            )
            return {"memories": [mem.model_dump(exclude_none=True) for mem in memories]}
        if method == "GET" and path == "/memories/counts":
            namespace = payload.get("namespace")
            counts = self.service.memory_counts(namespace)
            return {"counts": counts}
        if method == "GET" and path == "/triplets":
            namespace = payload.get("namespace")
            triplets = self.service.list_triplets(namespace)
            return {"triplets": [triplet.model_dump(exclude_none=True) for triplet in triplets]}
        raise ValueError(f"Unsupported route {method} {path}")


def create_app(service: MemoryService) -> Any:
    """Create a FastAPI application if FastAPI is installed, otherwise return a stub."""

    try:  # pragma: no cover - optional dependency path
        from fastapi import FastAPI, HTTPException
    except ImportError:  # pragma: no cover - executed in tests without fastapi
        return RestAPIStub(service)

    app = FastAPI(title="MeshMind API")

    @app.post("/memories")
    def create_memories(payload: Dict[str, Iterable[Dict[str, Any]]]):
        try:
            items = [MemoryPayload(**item) for item in payload.get("memories", [])]
        except Exception as exc:  # pragma: no cover - FastAPI handles validation
            raise HTTPException(status_code=400, detail=str(exc))
        uuids = service.ingest_memories(items)
        return {"uuids": uuids}

    @app.post("/triplets")
    def create_triplets(payload: Dict[str, Iterable[Dict[str, Any]]]):
        try:
            items = [TripletPayload(**item) for item in payload.get("triplets", [])]
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc))
        stored = service.ingest_triplets(items)
        return {"stored": stored}

    @app.post("/search")
    def search(payload: Dict[str, Any]):
        try:
            request = SearchPayload(**payload)
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc))
        results = service.search(request)
        return {"results": [mem.model_dump(exclude_none=True) for mem in results]}

    @app.get("/memories")
    def list_memories(
        namespace: str | None = None,
        entity_labels: List[str] | None = None,
        offset: int = 0,
        limit: int | None = None,
        query: str | None = None,
        use_search: bool | None = None,
    ):
        memories = service.list_memories(
            namespace,
            entity_labels,
            offset=offset,
            limit=limit,
            query=query,
            use_search=use_search,
        )
        return {"memories": [mem.model_dump(exclude_none=True) for mem in memories]}

    @app.get("/triplets")
    def list_triplets(namespace: str | None = None):
        triplets = service.list_triplets(namespace)
        return {"triplets": [triplet.model_dump(exclude_none=True) for triplet in triplets]}

    @app.get("/memories/counts")
    def memory_counts(namespace: str | None = None):
        return {"counts": service.memory_counts(namespace)}

    return app
