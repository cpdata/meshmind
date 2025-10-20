"""Abstract base class for graph database drivers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple
import uuid


class GraphDriver(ABC):
    """Abstract base class for graph database drivers."""

    VectorSearchResult = Tuple[Dict[str, Any], float]

    @abstractmethod
    def upsert_entity(self, label: str, name: str, props: Dict[str, Any]) -> None:
        """Insert or update an entity node."""
        raise NotImplementedError

    @abstractmethod
    def upsert_edge(self, subj: str, pred: str, obj: str, props: Dict[str, Any]) -> None:
        """Insert or update an edge between two entities."""
        raise NotImplementedError

    @abstractmethod
    def find(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        raise NotImplementedError

    @abstractmethod
    def get_entity(self, uid: str) -> Optional[Dict[str, Any]]:
        """Return a single entity by UUID, if it exists."""
        raise NotImplementedError

    @abstractmethod
    def list_entities(
        self,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Return entities, optionally filtered by namespace and label."""
        raise NotImplementedError

    def search_entities(
        self,
        query: Optional[str] = None,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Server-side memory search. Defaults to ``list_entities`` when unsupported."""

        return self.list_entities(
            namespace=namespace,
            entity_labels=entity_labels,
            offset=offset,
            limit=limit,
        )

    @abstractmethod
    def delete(self, uuid: uuid.UUID) -> None:
        """Delete a node or relationship by UUID."""
        raise NotImplementedError

    @abstractmethod
    def delete_triplet(self, subj: str, pred: str, obj: str) -> None:
        """Delete a relationship identified by subject/predicate/object."""

        raise NotImplementedError

    @abstractmethod
    def list_triplets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return stored triplets, optionally filtered by namespace."""

        raise NotImplementedError

    def count_entities(
        self, namespace: Optional[str] = None
    ) -> Dict[str, Dict[str, int]]:
        """Return memory counts grouped by namespace and entity label."""

        raise NotImplementedError

    def vector_search(
        self,
        query_embedding: Sequence[float],
        *,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        top_k: int = 10,
    ) -> List[VectorSearchResult]:
        """Compute cosine similarity against stored embeddings on the client side.

        Drivers with native vector capabilities should override this method with
        a backend implementation. The fallback retrieves matching entities and
        ranks them locally.
        """

        if top_k <= 0:
            return []
        embedding = list(query_embedding)
        if not embedding:
            return []

        try:
            candidates = self.list_entities(
                namespace=namespace,
                entity_labels=entity_labels,
            )
        except NotImplementedError:
            candidates = []

        if not candidates:
            return []

        from meshmind.core.similarity import cosine_similarity

        results: List[GraphDriver.VectorSearchResult] = []
        for candidate in candidates:
            stored = candidate.get("embedding")
            try:
                score = float(cosine_similarity(embedding, list(stored)))
            except Exception:
                continue
            results.append((dict(candidate), score))

        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]
