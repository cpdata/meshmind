"""Registry for entity and predicate models."""
from typing import Type, Optional, Dict, Set
from pydantic import BaseModel


class EntityRegistry:
    """Registry to manage Pydantic entity models."""
    _entities: Dict[str, Type[BaseModel]] = {}

    @classmethod
    def register(cls, model: Type[BaseModel]) -> None:
        """Register a Pydantic model as an entity."""
        cls._entities[model.__name__] = model

    @classmethod
    def model_for_label(cls, label: str) -> Optional[Type[BaseModel]]:
        """Get the model class for a given label."""
        return cls._entities.get(label)


class PredicateRegistry:
    """Registry to manage allowed predicate labels."""
    _predicates: Set[str] = set()

    @classmethod
    def add(cls, label: str) -> None:
        """Register a predicate label."""
        cls._predicates.add(label)

    @classmethod
    def allowed(cls, label: str) -> bool:
        """Check if a predicate label is allowed."""
        return label in cls._predicates