from argparse import Namespace
from io import StringIO

import pytest

from meshmind.cli import admin
from meshmind.cli.__main__ import serve_grpc_command
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
    admin.handle_maintenance(
        Namespace(reset=False, max_attempts=None, base_delay=None, run=None),
        stream=stream,
    )
    output = stream.getvalue()
    assert "events.test" in output


def test_handle_maintenance_overrides_and_runs(monkeypatch):
    original_max = admin.settings.MAINTENANCE_MAX_ATTEMPTS
    original_delay = admin.settings.MAINTENANCE_BASE_DELAY_SECONDS
    calls: list[str] = []

    def fake_consolidate():
        calls.append("consolidate")
        return {"merged": 1}

    monkeypatch.setattr(
        "meshmind.tasks.scheduled.consolidate_task", fake_consolidate
    )

    try:
        stream = StringIO()
        admin.handle_maintenance(
            Namespace(
                reset=False,
                max_attempts=5,
                base_delay=2.5,
                run="consolidate",
            ),
            stream=stream,
        )
        assert admin.settings.MAINTENANCE_MAX_ATTEMPTS == 5
        assert admin.settings.MAINTENANCE_BASE_DELAY_SECONDS == 2.5
        assert calls == ["consolidate"]
        output = stream.getvalue()
        assert '"task": "consolidate"' in output
        assert "MAINTENANCE_MAX_ATTEMPTS" in output
    finally:
        admin.settings.MAINTENANCE_MAX_ATTEMPTS = original_max
        admin.settings.MAINTENANCE_BASE_DELAY_SECONDS = original_delay


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


def test_serve_grpc_command_invokes_runtime(monkeypatch):
    drivers = []
    calls = []

    class DummyDriver:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    def fake_create_graph_driver(backend=None):  # noqa: ANN001 - signature match
        driver = DummyDriver()
        drivers.append((backend, driver))
        return driver

    def fake_serve_forever(service, host, port, shutdown_grace, **kwargs):  # noqa: ANN001
        calls.append({
            "service": service,
            "host": host,
            "port": port,
            "shutdown_grace": shutdown_grace,
        })

    monkeypatch.setattr("meshmind.cli.__main__.create_graph_driver", fake_create_graph_driver)
    monkeypatch.setattr("meshmind.cli.__main__.serve_forever", fake_serve_forever)

    args = Namespace(host="127.0.0.1", port=50052, backend="sqlite", shutdown_grace=1.5)

    serve_grpc_command(args)

    assert calls and calls[0]["host"] == "127.0.0.1"
    assert calls[0]["port"] == 50052
    assert abs(calls[0]["shutdown_grace"] - 1.5) < 1e-6
    assert drivers and drivers[0][0] == "sqlite"
    assert drivers[0][1].closed
