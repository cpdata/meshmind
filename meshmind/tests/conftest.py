import pytest

from meshmind.api.memory_manager import MemoryManager
from meshmind.api.service import MemoryService
from meshmind.core.embeddings import EncoderRegistry
from meshmind.core.types import Memory
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.testing import FakeMemgraphDriver, FakeRedisBroker


@pytest.fixture
def memory_factory():
    def _factory(name: str, **overrides):
        payload = {"namespace": "ns", "name": name, "entity_label": "Test"}
        payload.update(overrides)
        return Memory(**payload)

    return _factory


@pytest.fixture
def dummy_encoder():
    EncoderRegistry.clear()

    class _Encoder:
        def encode(self, texts):
            return [[1.0 if "apple" in text else 0.0] for text in texts]

    name = "dummy-encoder"
    EncoderRegistry.register(name, _Encoder())
    yield name
    EncoderRegistry.clear()


@pytest.fixture
def fake_memgraph_driver():
    return FakeMemgraphDriver()


@pytest.fixture
def fake_redis():
    return FakeRedisBroker()


@pytest.fixture
def in_memory_driver():
    return InMemoryGraphDriver()


@pytest.fixture
def memory_manager(in_memory_driver):
    return MemoryManager(in_memory_driver)


@pytest.fixture
def memory_service(memory_manager):
    return MemoryService(memory_manager)
