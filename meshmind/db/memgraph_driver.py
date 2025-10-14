"""Memgraph implementation of :class:`GraphDriver` using ``mgclient``."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

from meshmind.db.base_driver import GraphDriver

try:  # pragma: no cover - optional dependency
    import mgclient
except ImportError:  # pragma: no cover - optional dependency
    mgclient = None  # type: ignore


class MemgraphDriver(GraphDriver):
    """Memgraph driver implementation backed by ``mgclient``."""

    def __init__(self, uri: str, username: str = "", password: str = "") -> None:
        if mgclient is None:
            raise ImportError("mgclient is required for MemgraphDriver")

        self.uri = uri
        self.username = username
        self.password = password

        parsed = urlparse(uri)
        host = parsed.hostname or "localhost"
        port = parsed.port or 7687

        self._conn = mgclient.connect(  # type: ignore[union-attr]
            host=host,
            port=port,
            username=username or None,
            password=password or None,
        )
        self._cursor = self._conn.cursor()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _execute(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        params = params or {}
        self._cursor.execute(cypher, params)
        try:
            rows = self._cursor.fetchall()
            cols = [col[0] for col in self._cursor.description]
        except Exception:
            return []

        results: List[Dict[str, Any]] = []
        for row in rows:
            record: Dict[str, Any] = {}
            for idx, value in enumerate(row):
                record[cols[idx]] = value
            results.append(record)
        return results

    @staticmethod
    def _sanitize_predicate(predicate: str) -> str:
        return predicate.replace("`", "")

    @staticmethod
    def _normalize_node(node: Any) -> Dict[str, Any]:
        if hasattr(node, "properties"):
            try:
                return dict(node.properties)  # type: ignore[attr-defined]
            except Exception:
                pass
        if isinstance(node, dict):
            return dict(node)
        if hasattr(node, "_properties"):
            return dict(getattr(node, "_properties"))
        return {k: v for k, v in getattr(node, "__dict__", {}).items() if not k.startswith("_")}

    # ------------------------------------------------------------------
    # GraphDriver API
    # ------------------------------------------------------------------
    def upsert_entity(self, label: str, name: str, props: Dict[str, Any]) -> None:
        uid = props.get("uuid")
        cypher = (
            f"MERGE (n:{label} {{uuid: $uuid}})\n"
            f"SET n += $props"
        )
        params = {"uuid": str(uid), "props": props}
        self._execute(cypher, params)
        self._conn.commit()

    def upsert_edge(self, subj: str, pred: str, obj: str, props: Dict[str, Any]) -> None:
        predicate = self._sanitize_predicate(pred)
        cypher = (
            "MATCH (a {uuid: $subj}), (b {uuid: $obj})\n"
            f"MERGE (a)-[r:`{predicate}`]->(b)\n"
            "SET r += $props"
        )
        params = {"subj": str(subj), "obj": str(obj), "props": props}
        self._execute(cypher, params)
        self._conn.commit()

    def find(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._execute(cypher, params)

    def get_entity(self, uid: str) -> Optional[Dict[str, Any]]:
        records = self.find(
            "MATCH (m) WHERE m.uuid = $uuid RETURN m",
            {"uuid": str(uid)},
        )
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
        entities: List[Dict[str, Any]] = []
        for record in records:
            node = record.get("m", record)
            entities.append(self._normalize_node(node))
        return entities

    def delete(self, uuid: Any) -> None:
        cypher = "MATCH (n {uuid: $uuid}) DETACH DELETE n"
        params = {"uuid": str(uuid)}
        self._execute(cypher, params)
        self._conn.commit()

    def delete_triplet(self, subj: str, pred: str, obj: str) -> None:
        predicate = self._sanitize_predicate(pred)
        cypher = (
            "MATCH (a {uuid: $subj})-[r:`{predicate}`]->(b {uuid: $obj}) "
            "DELETE r"
        )
        params = {"subj": str(subj), "obj": str(obj)}
        self._execute(cypher, params)
        self._conn.commit()

    def list_triplets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        cypher = (
            "MATCH (a)-[r]->(b)\n"
            "WHERE $namespace IS NULL OR r.namespace = $namespace\n"
            "RETURN a.uuid AS subject, type(r) AS predicate, b.uuid AS object, "
            "r.namespace AS namespace, r.metadata AS metadata, r.reference_time AS reference_time"
        )
        params = {"namespace": namespace}
        return self._execute(cypher, params)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def vector_search(self, embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        from meshmind.core.similarity import cosine_similarity

        records = self.find(
            "MATCH (n) WHERE exists(n.embedding) RETURN n.embedding AS emb, n AS node",
            {},
        )
        scored = []
        for rec in records:
            emb = rec.get("emb")
            if not isinstance(emb, list):
                continue
            try:
                score = cosine_similarity(embedding, emb)
            except Exception:
                score = 0.0
            scored.append({"node": rec.get("node"), "score": float(score)})
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]
