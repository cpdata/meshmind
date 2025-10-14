from argparse import Namespace
from io import StringIO

import pytest

from meshmind.cli import admin
from meshmind.core.observability import telemetry
from meshmind.models.registry import PredicateRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    PredicateRegistry.clear()
    telemetry.reset()
    yield
    PredicateRegistry.clear()
    telemetry.reset()


def test_handle_predicates_add_list_remove():
    stream = StringIO()
    admin.handle_predicates(Namespace(add="LIKES", remove=None, list=False), stream=stream)
    assert "LIKES" in stream.getvalue()
    stream = StringIO()
    admin.handle_predicates(Namespace(add=None, remove="LIKES", list=False), stream=stream)
    assert "Removed" in stream.getvalue()
    stream = StringIO()
    admin.handle_predicates(Namespace(add=None, remove=None, list=True), stream=stream)
    assert "predicates" in stream.getvalue()


def test_handle_maintenance_outputs_snapshot():
    telemetry.increment("events.test")
    stream = StringIO()
    admin.handle_maintenance(Namespace(reset=False), stream=stream)
    output = stream.getvalue()
    assert "events.test" in output


def test_handle_graph_check_with_verify(monkeypatch):
    class DummyDriver:
        def verify_connectivity(self):
            return True

    monkeypatch.setattr(admin, "create_graph_driver", lambda **kwargs: DummyDriver())
    stream = StringIO()
    status = admin.handle_graph_check(Namespace(backend="neo4j"), stream=stream)
    assert status == 0
    assert "ok" in stream.getvalue()


def test_handle_counts_outputs_grouped(monkeypatch):
    class DummyDriver:
        def __init__(self):
            self.closed = False

        def count_entities(self, namespace=None):  # noqa: ARG002 - testing helper
            return {"demo": {"Note": 3}}

        def close(self):
            self.closed = True

    monkeypatch.setattr(admin, "create_graph_driver", lambda **kwargs: DummyDriver())
    stream = StringIO()
    status = admin.handle_counts(Namespace(backend="memory", namespace=None), stream=stream)

    assert status == 0
    assert "\"Note\": 3" in stream.getvalue()
