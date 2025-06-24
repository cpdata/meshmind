import json
import pytest
import openai

from meshmind.client import MeshMind
from meshmind.core.types import Memory
from meshmind.core.embeddings import EncoderRegistry
from meshmind.db.memgraph_driver import MemgraphDriver


class DummyEncoder:
    """Dummy encoder returning text lengths as embeddings."""
    def encode(self, texts):
        return [[len(text)] for text in texts]


class DummyChoice:
    def __init__(self, message):
        self.message = message

class DummyResponse:
    def __init__(self, arg_json):
        func_call = {'arguments': arg_json}
        self.choices = [DummyChoice({'function_call': func_call})]


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    """Patch OpenAI client to use DummyChat for responses."""
    class DummyChat:
        @staticmethod
        def create(model, messages, functions, function_call):
            names = [m['content'] for m in messages if m['role'] == 'user']
            items = [{'name': n, 'entity_label': 'Memory'} for n in names]
            arg_json = json.dumps({'memories': items})
            return DummyResponse(arg_json)
    class DummyModelClient:
        def __init__(self):
            self.responses = DummyChat
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyModelClient())
    return None


def test_extract_memories_basic(tmp_path):
    # Register dummy encoder
    EncoderRegistry.register('text-embedding-3-small', DummyEncoder())
    mm = MeshMind()
    # override default llm_client to use dummy
    mm.llm_client = openai.OpenAI()
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


def test_extract_invalid_label(monkeypatch):
    # Monkeypatch to return an entry with invalid label
    def bad_create(*args, **kwargs):
        arg_json = json.dumps({'memories': [{'name': 'x', 'entity_label': 'Bad'}]})
        return DummyResponse(arg_json)
    from openai import OpenAI
    llm_client = OpenAI()
    monkeypatch.setattr(llm_client.responses, 'create', bad_create)
    EncoderRegistry.register('text-embedding-3-small', DummyEncoder())
    mm = MeshMind(llm_client=llm_client)
    with pytest.raises(ValueError) as e:
        mm.extract_memories(
            instructions='Extract:',
            namespace='ns',
            entity_types=[Memory],
            content=['x'],
        )
    assert 'Invalid entity_label' in str(e.value)