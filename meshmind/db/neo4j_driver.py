"""Neo4j implementation of :class:`GraphDriver` using the official driver."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from meshmind.db.base_driver import GraphDriver

try:  # pragma: no cover - optional dependency
    from neo4j import GraphDatabase  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    GraphDatabase = None  # type: ignore


class Neo4jGraphDriver(GraphDriver):
    """GraphDriver backed by Neo4j via the ``neo4j`` Python driver."""

    def __init__(self, uri: str, username: str = "neo4j", password: str = "") -> None:
        if GraphDatabase is None:
            raise ImportError("neo4j driver is required for Neo4jGraphDriver")
        auth = None
        if username or password:
            auth = (username or None, password or None)
        self._driver = GraphDatabase.driver(uri, auth=auth)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        params = params or {}
        with self._driver.session() as session:  # type: ignore[attr-defined]
            result = session.run(cypher, **params)
            records = []
            for record in result:
                records.append(record.data())
            return records

    @staticmethod
    def _normalize_node(node: Any) -> Dict[str, Any]:
        if hasattr(node, "_properties"):
            return dict(node._properties)  # type: ignore[attr-defined]
        if isinstance(node, dict):
            return dict(node)
        return {k: v for k, v in getattr(node, "__dict__", {}).items() if not k.startswith("_")}

    # ------------------------------------------------------------------
    # GraphDriver API
    # ------------------------------------------------------------------
    def upsert_entity(self, label: str, name: str, props: Dict[str, Any]) -> None:
        cypher = (
            f"MERGE (n:{label} {{uuid: $uuid}})\n"
            "SET n += $props"
        )
        params = {"uuid": str(props.get("uuid")), "props": props}
        self._run(cypher, params)

    def upsert_edge(self, subj: str, pred: str, obj: str, props: Dict[str, Any]) -> None:
        predicate = pred.replace("`", "")
        cypher = (
            "MATCH (a {uuid: $subj}), (b {uuid: $obj})\n"
            f"MERGE (a)-[r:`{predicate}`]->(b)\n"
            "SET r += $props"
        )
        params = {"subj": str(subj), "obj": str(obj), "props": props}
        self._run(cypher, params)

    def find(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._run(cypher, params)

    def get_entity(self, uid: str) -> Optional[Dict[str, Any]]:
        records = self.find("MATCH (m) WHERE m.uuid = $uuid RETURN m", {"uuid": str(uid)})
        if not records:
            return None
        node = records[0].get("m", records[0])
        return self._normalize_node(node)

    def list_entities(
        self,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        cypher = (
            "MATCH (m)\n"
            "WHERE ($namespace IS NULL OR m.namespace = $namespace)\n"
            "AND ($labels IS NULL OR m.entity_label IN $labels)\n"
            "RETURN m"
        )
        params = {
            "namespace": namespace,
            "labels": list(entity_labels) if entity_labels else None,
        }
        records = self.find(cypher, params)
        return [self._normalize_node(rec.get("m", rec)) for rec in records]

    def delete(self, uuid: Any) -> None:
        self._run("MATCH (m {uuid: $uuid}) DETACH DELETE m", {"uuid": str(uuid)})

    def delete_triplet(self, subj: str, pred: str, obj: str) -> None:
        predicate = pred.replace("`", "")
        cypher = (
            f"MATCH (a {{uuid: $subj}})-[r:`{predicate}`]->(b {{uuid: $obj}})"
            " DELETE r"
        )
        self._run(cypher, {"subj": str(subj), "obj": str(obj)})

    def list_triplets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        cypher = (
            "MATCH (a)-[r]->(b)\n"
            "WHERE $namespace IS NULL OR r.namespace = $namespace\n"
            "RETURN a.uuid AS subject, type(r) AS predicate, b.uuid AS object, "
            "r.namespace AS namespace, r.metadata AS metadata, r.reference_time AS reference_time"
        )
        params = {"namespace": namespace}
        return self.find(cypher, params)

    def close(self) -> None:
        self._driver.close()

    def verify_connectivity(self) -> bool:
        """Use the Neo4j driver to verify connectivity."""

        checker = getattr(self._driver, "verify_connectivity", None)
        if callable(checker):
            checker()
            return True
        try:
            self._run("RETURN 1 AS ok")
        except Exception:
            return False
        return True
