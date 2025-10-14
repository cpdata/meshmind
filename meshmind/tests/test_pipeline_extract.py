import json

import pytest

from meshmind.client import MeshMind
from meshmind.core.types import Memory
from meshmind.core.embeddings import EncoderRegistry


class DummyEncoder:
    """Dummy encoder returning text lengths as embeddings."""
    def encode(self, texts):
        return [[len(text)] for text in texts]


class DummyResponse:
    def __init__(self, payload):
        self.choices = [type('Choice', (), {'message': payload})]


class DummyLLMClient:
    class responses:  # type: ignore[assignment]
        @staticmethod
        def create(model, messages, functions, function_call):
            names = [m['content'] for m in messages if m['role'] == 'user']
            items = [{'name': n, 'entity_label': 'Memory'} for n in names]
            arg_json = json.dumps({'memories': items})
            return DummyResponse({'function_call': {'arguments': arg_json}})


def test_extract_memories_basic(tmp_path):
    # Register dummy encoder
    EncoderRegistry.clear()
    EncoderRegistry.register('text-embedding-3-small', DummyEncoder())
    mm = MeshMind(llm_client=DummyLLMClient())
    # Run extraction
    texts = ['alpha', 'beta']
    results = mm.extract_memories(
        instructions='Extract memories:',
        namespace='ns',
        entity_types=[Memory],
        content=texts,
    )
    assert len(results) == 2
    for mem, text in zip(results, texts):
        assert isinstance(mem, Memory)
        assert mem.name == text
        assert mem.namespace == 'ns'
        # Embedding via DummyEncoder: length of name
        assert mem.embedding == [len(text)]


def test_extract_invalid_label():
    class BadLLMClient:
        class responses:  # type: ignore[assignment]
            @staticmethod
            def create(*args, **kwargs):
                arg_json = json.dumps({'memories': [{'name': 'x', 'entity_label': 'Bad'}]})
                return DummyResponse({'function_call': {'arguments': arg_json}})

    EncoderRegistry.clear()
    EncoderRegistry.register('text-embedding-3-small', DummyEncoder())
    mm = MeshMind(llm_client=BadLLMClient())
    with pytest.raises(ValueError) as e:
        mm.extract_memories(
            instructions='Extract:',
            namespace='ns',
            entity_types=[Memory],
            content=['x'],
        )
    assert 'Invalid entity_label' in str(e.value)
