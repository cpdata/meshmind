import argparse
import json

import pytest

from meshmind.api.memory_manager import MemoryManager
from meshmind.api.rest import RestAPIStub
from meshmind.api.service import MemoryService
from meshmind.cli import admin
from meshmind.core.types import Memory
from meshmind.db.in_memory_driver import InMemoryGraphDriver


@pytest.fixture()
def populated_service():
    driver = InMemoryGraphDriver()
    manager = MemoryManager(driver)
    service = MemoryService(manager)

    mem_a = Memory(namespace="docs", name="Alpha", entity_label="Note", metadata={"content": "A"})
    mem_b = Memory(namespace="docs", name="Beta", entity_label="Note", metadata={"content": "B"})
    mem_c = Memory(namespace="support", name="Ticket", entity_label="Case")

    manager.add_memory(mem_a)
    manager.add_memory(mem_b)
    manager.add_memory(mem_c)

    return driver, service


def test_rest_counts_endpoint_returns_totals(populated_service):
    driver, service = populated_service
    api = RestAPIStub(service)

    response = api.dispatch("GET", "/memories/counts", {"namespace": "docs"})

    assert "counts" in response
    assert response["counts"]["docs"]["Note"] == 2
    assert "support" not in response["counts"]


def test_cli_admin_counts_reports_json(populated_service, monkeypatch, capsys):
    driver, service = populated_service
    monkeypatch.setattr(admin, "create_graph_driver", lambda backend=None: driver)

    args = argparse.Namespace(backend="memory", namespace=None)
    exit_code = admin.handle_counts(args)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["docs"]["Note"] == 2
    assert payload["support"]["Case"] == 1
