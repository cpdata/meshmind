import pytest

from meshmind.core.embeddings import EncoderRegistry
from meshmind.core.types import Memory


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

    class DummyEncoder:
        def encode(self, texts):
            return [[1.0 if "apple" in text else 0.0] for text in texts]

    name = "dummy-encoder"
    EncoderRegistry.register(name, DummyEncoder())
    yield name
    EncoderRegistry.clear()
