"""Shared logging and metrics utilities for MeshMind pipelines."""
from __future__ import annotations

import logging
from collections import defaultdict
from contextlib import contextmanager
from time import perf_counter
from typing import Any, Dict, Iterable

_LOGGER_NAME = "meshmind"
logger = logging.getLogger(_LOGGER_NAME)
if not logger.handlers:  # pragma: no cover - avoid duplicate handlers in tests
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Telemetry:
    """Lightweight in-memory metrics collector."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = defaultdict(int)
        self._durations: Dict[str, list[float]] = defaultdict(list)
        self._gauges: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Counter helpers
    # ------------------------------------------------------------------
    def increment(self, metric: str, value: int = 1) -> None:
        self._counters[metric] += value

    def gauge(self, metric: str, value: float) -> None:
        self._gauges[metric] = value

    def observe(self, metric: str, value: float) -> None:
        self._durations[metric].append(value)

    @contextmanager
    def track_duration(self, metric: str):
        start = perf_counter()
        try:
            yield
        finally:
            elapsed = perf_counter() - start
            self.observe(metric, elapsed)

    def extend_counter(self, metric: str, values: Iterable[Any]) -> None:
        count = sum(1 for _ in values)
        self.increment(metric, count)

    # ------------------------------------------------------------------
    # Snapshot helpers
    # ------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "durations": {k: list(v) for k, v in self._durations.items()},
            "gauges": dict(self._gauges),
        }

    def reset(self) -> None:
        self._counters.clear()
        self._durations.clear()
        self._gauges.clear()


telemetry = Telemetry()


def log_event(event: str, **fields: Any) -> None:
    """Emit a structured log entry and update a counter for the event."""

    telemetry.increment(f"events.{event}")
    if fields:
        formatted = " ".join(f"{key}={value}" for key, value in fields.items())
        logger.info("event=%s %s", event, formatted)
    else:
        logger.info("event=%s", event)
