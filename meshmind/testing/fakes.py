"""Testing doubles for MeshMind components and external services."""
from __future__ import annotations

import json
from collections import defaultdict, deque
from types import SimpleNamespace
from typing import Any, Deque, Dict, Iterable, List, Optional

from meshmind.db.in_memory_driver import InMemoryGraphDriver


class FakeMemgraphDriver(InMemoryGraphDriver):
    """In-memory substitute that records Cypher interactions for assertions."""

    def __init__(self) -> None:
        super().__init__()
        self.cypher_calls: List[tuple[str, Dict[str, Any]]] = []

    def find(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        self.cypher_calls.append((cypher, dict(params)))
        return super().find(cypher, params)


class FakeRedisBroker:
    """Lightweight Redis replacement implementing the few operations we use."""

    def __init__(self) -> None:
        self._kv: Dict[str, Any] = {}
        self._lists: Dict[str, Deque[Any]] = defaultdict(deque)
        self._pubsub: Dict[str, List[Any]] = defaultdict(list)

    # Key/value helpers -------------------------------------------------
    def get(self, key: str) -> Any:
        return self._kv.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> None:  # noqa: ARG002 - expiry unused
        self._kv[key] = value

    def delete(self, *keys: str) -> int:
        removed = 0
        for key in keys:
            if key in self._kv:
                del self._kv[key]
                removed += 1
            if key in self._lists:
                del self._lists[key]
                removed += 1
        return removed

    # List helpers ------------------------------------------------------
    def lpush(self, key: str, *values: Any) -> int:
        lst = self._lists[key]
        for value in values:
            lst.appendleft(value)
        return len(lst)

    def rpush(self, key: str, *values: Any) -> int:
        lst = self._lists[key]
        for value in values:
            lst.append(value)
        return len(lst)

    def lrange(self, key: str, start: int, stop: int) -> List[Any]:
        lst = list(self._lists[key])
        if stop == -1:
            stop = len(lst)
        return lst[start:stop + 1]

    # Pub/Sub helpers ---------------------------------------------------
    def publish(self, channel: str, message: Any) -> int:
        self._pubsub[channel].append(message)
        return len(self._pubsub[channel])


class FakeEmbeddingEncoder:
    """Deterministic encoder that hashes text into simple float vectors."""

    def __init__(self, scale: float = 1.0) -> None:
        self.scale = scale

    def encode(self, texts: Iterable[str] | str) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        vectors: List[List[float]] = []
        for text in texts:
            total = sum(ord(ch) for ch in text)
            vectors.append([self.scale * (total % 101) / 100.0])
        return vectors


class FakeLLMClient:
    """OpenAI-compatible stub that records override usage during tests."""

    class _Proxy:
        def __init__(self, parent: "FakeLLMClient", interface: str) -> None:
            self._parent = parent
            self._interface = interface

        def create(
            self,
            *,
            operation: str | None = None,
            model: str | None = None,
            base_url: str | None = None,
            **kwargs: Any,
        ) -> Any:
            return self._parent._create(
                self._interface,
                operation or ("embedding" if self._interface == "embeddings" else "extraction"),
                model,
                base_url,
                **kwargs,
            )

    def __init__(
        self,
        *,
        models: Dict[str, str] | None = None,
        base_urls: Dict[str, Optional[str]] | None = None,
        api_key: str | None = None,
        call_log: List[Dict[str, Any]] | None = None,
    ) -> None:
        self._models: Dict[str, str] = {"default": "gpt-5-nano"}
        if models:
            for key, value in models.items():
                if value:
                    self._models[key] = value
        self._base_urls: Dict[str, Optional[str]] = {"default": None}
        if base_urls:
            for key, value in base_urls.items():
                self._base_urls[key] = value
        self.api_key = api_key or ""
        self.calls: List[Dict[str, Any]] = call_log if call_log is not None else []
        self.last_override: Dict[str, Any] | None = None
        self.config = SimpleNamespace(
            model_for=self._model_for,
            base_url_for=self._base_url_for,
        )
        self.responses = FakeLLMClient._Proxy(self, "responses")
        self.embeddings = FakeLLMClient._Proxy(self, "embeddings")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _model_for(self, operation: str, fallback: str | None = None) -> str:
        return (
            self._models.get(operation)
            or self._models.get("default")
            or fallback
            or "gpt-5-nano"
        )

    def _base_url_for(self, operation: str) -> Optional[str]:
        return self._base_urls.get(operation) or self._base_urls.get("default")

    def with_overrides(
        self,
        *,
        models: Dict[str, Optional[str]] | None = None,
        base_urls: Dict[str, Optional[str]] | None = None,
        api_key: str | None = None,
    ) -> "FakeLLMClient":
        new_models = dict(self._models)
        if models:
            for key, value in models.items():
                if value:
                    new_models[key] = value
        new_base_urls = dict(self._base_urls)
        if base_urls:
            for key, value in base_urls.items():
                new_base_urls[key] = value
        override_details = {
            "models": models,
            "base_urls": base_urls,
            "api_key": api_key,
        }
        child = FakeLLMClient(
            models=new_models,
            base_urls=new_base_urls,
            api_key=api_key or self.api_key,
            call_log=self.calls,
        )
        self.last_override = override_details
        child.last_override = override_details
        return child

    def _create(
        self,
        interface: str,
        operation: str,
        model: str | None,
        base_url: str | None,
        **kwargs: Any,
    ) -> Any:
        resolved_model = model or self._model_for(operation)
        resolved_base = base_url if base_url not in ("", None) else self._base_url_for(operation)
        payload = {
            "interface": interface,
            "operation": operation,
            "model": resolved_model,
            "base_url": resolved_base,
            "kwargs": kwargs,
        }
        self.calls.append(payload)

        # Construct a synthetic response compatible with llm_rerank expectations.
        order = []
        inputs = kwargs.get("input", [])
        if inputs:
            first = inputs[0]
            content = first.get("content") if isinstance(first, dict) else None
            if isinstance(content, str):
                lines = content.splitlines()
            elif isinstance(content, list):
                lines = [part.get("text", "") for part in content if isinstance(part, dict)]
            else:
                lines = []
            for line in lines:
                prefix = line.split(":", 1)[0]
                if prefix.isdigit():
                    order.append(int(prefix))
        if not order:
            candidate_count = kwargs.get("candidate_count", 0)
            if candidate_count:
                order = list(range(candidate_count))
            else:
                order = [0]

        response_text = json.dumps({"order": order})
        return SimpleNamespace(
            output=[
                SimpleNamespace(
                    content=[SimpleNamespace(text=response_text)]
                )
            ]
        )

