"""Abstract base class for graph database drivers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence
import uuid


class GraphDriver(ABC):
    """Abstract base class for graph database drivers."""

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
