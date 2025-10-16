"""Bootstrap helpers for wiring encoders and registries."""
from __future__ import annotations

import warnings
from typing import Iterable, Sequence, Type

from pydantic import BaseModel

from meshmind.core.config import settings
from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder
from meshmind.core.types import Memory
from meshmind.models.registry import EntityRegistry, PredicateRegistry


def bootstrap_encoders(default_models: Sequence[str] | None = None) -> None:
    """Ensure a default set of embedding encoders are registered."""

    models = list(default_models) if default_models else [settings.EMBEDDING_MODEL]
    for model_name in models:
        if EncoderRegistry.is_registered(model_name):
            continue
        try:
            EncoderRegistry.register(model_name, OpenAIEmbeddingEncoder(model_name))
        except ImportError as exc:
            warnings.warn(
                f"Skipping registration of OpenAI encoder '{model_name}': {exc}",
                RuntimeWarning,
                stacklevel=2,
            )


def bootstrap_entities(entity_models: Iterable[Type[BaseModel]] | None = None) -> None:
    """Register default entity models used throughout the application."""

    models = list(entity_models) if entity_models else [Memory]
    for model in models:
        EntityRegistry.register(model)


def register_predicates(predicates: Iterable[str]) -> None:
    """Register predicate labels in the global predicate registry."""

    for predicate in predicates:
        PredicateRegistry.add(predicate)

