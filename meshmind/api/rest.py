"""REST adapters for the :mod:`meshmind` service layer."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from fastapi import FastAPI, HTTPException, Query

from meshmind.api.service import MemoryPayload, MemoryService, SearchPayload, TripletPayload


def create_app(service: MemoryService) -> Any:
    """Create a FastAPI application exposing MeshMind service routes."""

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
        entity_labels: List[str] | None = Query(default=None),
        offset: int = 0,
        limit: int | None = None,
        query: str | None = None,
        use_search: bool | None = None,
    ):
        labels: List[str] | None
        if entity_labels is None:
            labels = None
        elif isinstance(entity_labels, str):  # pragma: no cover - defensive guard
            labels = [entity_labels]
        else:
            labels = list(entity_labels)

        memories = service.list_memories(
            namespace,
            labels,
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
