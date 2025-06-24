import pytest

from meshmind.core.embeddings import EncoderRegistry, OpenAIEmbeddingEncoder, SentenceTransformerEncoder


class DummyEncoder:
    """Simple dummy encoder for testing."""
    def __init__(self):
        pass

    def encode(self, texts):
        # Return list of lengths of each text as embedding
        return [[len(text)] for text in texts]


def test_registry_register_and_get():
    # Register dummy encoder
    EncoderRegistry.register('dummy', DummyEncoder())
    encoder = EncoderRegistry.get('dummy')
    assert isinstance(encoder, DummyEncoder)
    # Test encode functionality
    texts = ['hello', 'world']
    embeddings = encoder.encode(texts)
    assert embeddings == [[5], [5]]

def test_registry_get_missing():
    with pytest.raises(KeyError):
        EncoderRegistry.get('nonexistent')