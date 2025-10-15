import pytest

from meshmind.db import neo4j_driver


def test_verify_connectivity_uses_driver(monkeypatch):
    class DummySession:
        def run(self, cypher, **params):
            return []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class DummyNeo4jDriver:
        def __init__(self, uri, auth=None):
            self.uri = uri
            self.auth = auth
            self.connected = False

        def session(self):
            return DummySession()

        def verify_connectivity(self):
            self.connected = True
            return True

        def close(self):
            pass

    class DummyGraphDatabase:
        @staticmethod
        def driver(uri, auth=None):
            return DummyNeo4jDriver(uri, auth)

    monkeypatch.setattr(neo4j_driver, "GraphDatabase", DummyGraphDatabase)
    driver = neo4j_driver.Neo4jGraphDriver("bolt://localhost:7687", "neo4j", "pass")
    assert driver.verify_connectivity() is True
