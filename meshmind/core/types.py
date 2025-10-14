from __future__ import annotations
from datetime import datetime
from typing import Any, Optional, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Memory(BaseModel):
    """
    Core memory data structure representing a unit of knowledge.
    """
    uuid: UUID = Field(default_factory=uuid4)
    namespace: str
    name: str
    entity_label: str
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    reference_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    importance: Optional[float] = None
    ttl_seconds: Optional[int] = None


class Triplet(BaseModel):
    """
    Graph triplet linking two entities via a predicate.
    """
    subject: str
    predicate: str
    object: str
    namespace: str
    entity_label: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    reference_time: Optional[datetime] = None


class SearchConfig(BaseModel):
    """
    Configuration for search queries, including encoder, filters, and weights.
    """
    encoder: str = "text-embedding-3-small"
    top_k: int = 20
    rerank_k: int = 10
    rerank_model: Optional[str] = None
    filters: Optional[dict[str, Any]] = None
    hybrid_weights: Tuple[float, float] = (0.5, 0.5)