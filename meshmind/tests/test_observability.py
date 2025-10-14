import pytest

from meshmind.core.observability import log_event, telemetry
from meshmind.pipeline.store import store_memories


@pytest.fixture(autouse=True)
def reset_telemetry():
    telemetry.reset()
    yield
    telemetry.reset()


def test_log_event_increments_counter():
    log_event("unit.test", value=1)
    snapshot = telemetry.snapshot()
    assert snapshot["counters"]["events.unit.test"] == 1


def test_store_memories_tracks_metrics(memory_factory, in_memory_driver):
    memories = [memory_factory("one"), memory_factory("two")]
    store_memories(memories, in_memory_driver)
    snapshot = telemetry.snapshot()
    assert snapshot["counters"]["pipeline.store.memories.stored"] == 2
