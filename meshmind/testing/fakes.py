"""Testing doubles for MeshMind components and external services."""
from __future__ import annotations

from collections import defaultdict, deque
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
