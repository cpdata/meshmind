from meshmind.llm_client import DEFAULT_MODEL, LLMClient, LLMConfig


class DummyResponses:
    def __init__(self, store):
        self._store = store

    def create(self, **kwargs):
        self._store.append(("responses", kwargs))
        return {"kwargs": kwargs}


class DummyEmbeddings:
    def __init__(self, store):
        self._store = store

    def create(self, **kwargs):
        self._store.append(("embeddings", kwargs))
        return {"kwargs": kwargs}


def test_llm_config_override_models():
    config = LLMConfig(api_key="key")
    overridden = config.override(models={"extraction": "custom"})
    assert overridden.model_for("extraction") == "custom"
    assert overridden.model_for("rerank") == DEFAULT_MODEL


def test_llm_client_applies_operation_defaults(monkeypatch):
    calls = []

    class DummyOpenAI:  # pragma: no cover - construction only used in test
        def __init__(self, **kwargs):
            calls.append(kwargs)
            self.responses = DummyResponses(calls)
            self.embeddings = DummyEmbeddings(calls)

    monkeypatch.setattr("meshmind.llm_client._OpenAI", DummyOpenAI)

    config = LLMConfig(
        api_key="token",
        base_urls={"default": None, "extraction": "https://extract"},
        models={"default": DEFAULT_MODEL, "embedding": "embed-model"},
    )
    client = LLMClient(config)
    client.responses.create(messages=[{"role": "user", "content": "hi"}])
    assert calls[0]["base_url"] == "https://extract"
    responses_kwargs = calls[1][1]
    assert responses_kwargs["model"] == DEFAULT_MODEL

    client.embeddings.create(input=["text"])
    assert calls[-1][0] == "embeddings"
    embeddings_kwargs = calls[-1][1]
    assert embeddings_kwargs["model"] == "embed-model"
