"""Abstract base class for graph database drivers."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
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
    def delete(self, uuid: uuid.UUID) -> None:
        """Delete a node or relationship by UUID."""
        raise NotImplementedError