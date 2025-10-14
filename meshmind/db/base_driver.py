"""Abstract base class for graph database drivers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
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
    def list_entities(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return entities, optionally filtered by namespace."""
        raise NotImplementedError

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
