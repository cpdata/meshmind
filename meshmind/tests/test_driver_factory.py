import pytest

from meshmind.db.factory import create_graph_driver, graph_driver_factory
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.db.sqlite_driver import SQLiteGraphDriver


def test_create_graph_driver_memory():
    driver = create_graph_driver(backend="memory")
    assert isinstance(driver, InMemoryGraphDriver)


def test_create_graph_driver_sqlite(tmp_path):
    path = tmp_path / "graph.db"
    driver = create_graph_driver(backend="sqlite", path=str(path))
    try:
        assert isinstance(driver, SQLiteGraphDriver)
    finally:
        driver.close()


def test_graph_driver_factory_callable():
    factory = graph_driver_factory(backend="memory")
    driver = factory()
    assert isinstance(driver, InMemoryGraphDriver)


def test_create_graph_driver_invalid_backend():
    with pytest.raises(ValueError):
        create_graph_driver(backend="unknown")
