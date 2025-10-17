"""Live integration tests exercising provisioned services."""
from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Iterator
from urllib.parse import urlparse
from uuid import uuid4

import pytest

from meshmind.db.memgraph_driver import MemgraphDriver
from meshmind.db.neo4j_driver import Neo4jGraphDriver

try:  # pragma: no cover - optional dependency
    import mgclient  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    mgclient = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from neo4j import GraphDatabase  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    GraphDatabase = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import redis  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    redis = None  # type: ignore

INTEGRATION_MARK = pytest.mark.integration


def _require_package(module: object | None, name: str) -> None:
    if module is None:
        pytest.skip(f"{name} package not installed; install optional dependencies")


def _wait_for_port(host: str, port: int, *, timeout: float = 15.0) -> None:
    """Poll until ``host:port`` becomes reachable."""

    import socket

    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            try:
                if sock.connect_ex((host, port)) == 0:
                    return
            except OSError:
                pass
        time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {host}:{port}")


@contextmanager
def _cleanup_namespace_memgraph(driver: MemgraphDriver, namespace: str) -> Iterator[None]:
    try:
        yield
    finally:
        driver.find(
            "MATCH (n) WHERE n.namespace = $namespace DETACH DELETE n",
            {"namespace": namespace},
        )
        driver._conn.commit()  # type: ignore[attr-defined]


@contextmanager
def _cleanup_namespace_neo4j(driver: Neo4jGraphDriver, namespace: str) -> Iterator[None]:
    try:
        yield
    finally:
        driver.find(
            "MATCH (n) WHERE n.namespace = $namespace DETACH DELETE n",
            {"namespace": namespace},
        )


@pytest.fixture(scope="module")
def live_memgraph() -> Iterator[MemgraphDriver]:
    _require_package(mgclient, "pymgclient")
    uri = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
    username = os.getenv("MEMGRAPH_USERNAME", "")
    password = os.getenv("MEMGRAPH_PASSWORD", "")
    parsed = urlparse(uri)
    host = parsed.hostname or "localhost"
    port = parsed.port or 7687
    try:
        _wait_for_port(host, port)
    except RuntimeError as exc:
        pytest.skip(f"Memgraph unavailable: {exc}")
    driver = MemgraphDriver(uri, username, password)
    try:
        yield driver
    finally:
        driver._conn.close()  # type: ignore[attr-defined]


@pytest.fixture(scope="module")
def live_neo4j() -> Iterator[Neo4jGraphDriver]:
    _require_package(GraphDatabase, "neo4j")
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7688")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "meshminD123")
    parsed = urlparse(uri)
    host = parsed.hostname or "localhost"
    port = parsed.port or 7687
    try:
        _wait_for_port(host, port)
    except RuntimeError as exc:
        pytest.skip(f"Neo4j unavailable: {exc}")
    driver = Neo4jGraphDriver(uri, username, password)
    try:
        yield driver
    finally:
        driver.close()


@pytest.fixture(scope="module")
def live_redis() -> Iterator["redis.Redis"]:  # type: ignore[name-defined]
    _require_package(redis, "redis")
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    client = redis.Redis.from_url(url, decode_responses=True)
    try:
        if not client.ping():
            pytest.skip("Redis ping failed")
    except Exception as exc:  # pragma: no cover - connection specific
        pytest.skip(f"Redis unavailable: {exc}")
    client.flushdb()
    try:
        yield client
    finally:
        client.flushdb()
        client.close()


@INTEGRATION_MARK
@pytest.mark.usefixtures("live_memgraph")
def test_memgraph_driver_live_roundtrip(live_memgraph: MemgraphDriver) -> None:
    namespace = f"itest-{uuid4()}"
    payload = {
        "uuid": str(uuid4()),
        "namespace": namespace,
        "name": "integration-memgraph",
        "entity_label": "Note",
        "metadata": {"content": "hello memgraph"},
    }
    with _cleanup_namespace_memgraph(live_memgraph, namespace):
        live_memgraph.upsert_entity("Note", payload["name"], payload)
        entity = live_memgraph.get_entity(payload["uuid"])
        assert entity is not None
        assert entity.get("name") == payload["name"]
        triplet_props = {
            "namespace": namespace,
            "metadata": {"kind": "link"},
        }
        other_uuid = str(uuid4())
        live_memgraph.upsert_entity(
            "Note",
            "integration-other",
            {
                "uuid": other_uuid,
                "namespace": namespace,
                "name": "integration-other",
                "entity_label": "Note",
            },
        )
        live_memgraph.upsert_edge(payload["uuid"], "related_to", other_uuid, triplet_props)
        triplets = live_memgraph.list_triplets(namespace)
        assert triplets and triplets[0]["predicate"] == "related_to"
        counts = live_memgraph.count_entities(namespace)
        assert namespace in counts
        live_memgraph.delete_triplet(payload["uuid"], "related_to", other_uuid)
        live_memgraph.delete(payload["uuid"])
        live_memgraph.delete(other_uuid)


@INTEGRATION_MARK
@pytest.mark.usefixtures("live_neo4j")
def test_neo4j_driver_live_roundtrip(live_neo4j: Neo4jGraphDriver) -> None:
    namespace = f"itest-{uuid4()}"
    payload = {
        "uuid": str(uuid4()),
        "namespace": namespace,
        "name": "integration-neo4j",
        "entity_label": "Note",
        "metadata": {"content": "hello neo4j"},
    }
    with _cleanup_namespace_neo4j(live_neo4j, namespace):
        live_neo4j.upsert_entity("Note", payload["name"], payload)
        entity = live_neo4j.get_entity(payload["uuid"])
        assert entity is not None
        assert entity.get("name") == payload["name"]
        live_neo4j.upsert_edge(payload["uuid"], "related_to", payload["uuid"], {"namespace": namespace})
        triplets = live_neo4j.list_triplets(namespace)
        assert any(row["predicate"] == "related_to" for row in triplets)
        counts = live_neo4j.count_entities(namespace)
        assert namespace in counts
        live_neo4j.delete_triplet(payload["uuid"], "related_to", payload["uuid"])
        live_neo4j.delete(payload["uuid"])


@INTEGRATION_MARK
def test_redis_broker_live_roundtrip(live_redis: "redis.Redis") -> None:  # type: ignore[name-defined]
    live_redis.set("meshmind:test", "online")
    assert live_redis.get("meshmind:test") == "online"
    live_redis.lpush("meshmind:queue", "a", "b")
    assert live_redis.lrange("meshmind:queue", 0, -1) == ["b", "a"]
    assert live_redis.delete("meshmind:test") == 1
