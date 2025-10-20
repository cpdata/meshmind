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
        *,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if limit is not None and limit <= 0:
            return []
        clauses = ["($namespace IS NULL OR m.namespace = $namespace)"]
        clauses.append("($labels IS NULL OR m.entity_label IN $labels)")
        cypher = ["MATCH (m)"]
        cypher.append("WHERE " + " AND ".join(clauses))
        cypher.append("RETURN m")
        cypher.append("ORDER BY m.namespace, m.entity_label, m.name")
        cypher.append("SKIP $offset")
        if limit is not None:
            cypher.append("LIMIT $limit")
        params = {
            "namespace": namespace,
            "labels": list(entity_labels) if entity_labels else None,
            "offset": max(offset, 0),
        }
        if limit is not None:
            params["limit"] = limit
        records = self.find("\n".join(cypher), params)
        return [self._normalize_node(rec.get("m", rec)) for rec in records]

    def search_entities(
        self,
        query: Optional[str] = None,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if limit is not None and limit <= 0:
            return []
        clauses = ["($namespace IS NULL OR m.namespace = $namespace)"]
        clauses.append("($labels IS NULL OR m.entity_label IN $labels)")
        params = {
            "namespace": namespace,
            "labels": list(entity_labels) if entity_labels else None,
            "offset": max(offset, 0),
            "search": query.lower() if query else None,
        }
        text_clause = (
            "($search IS NULL OR "
            "toLower(coalesce(m.name, '')) CONTAINS $search OR "
            "toLower(coalesce(m.content, '')) CONTAINS $search OR "
            "toLower(coalesce(m.description, '')) CONTAINS $search OR "
            "($search IS NOT NULL AND exists(m.metadata) AND "
            "any(value IN values(m.metadata) WHERE toLower(toString(value)) CONTAINS $search))"
            ")"
        )
        clauses.append(text_clause)
        cypher = ["MATCH (m)"]
        cypher.append("WHERE " + " AND ".join(clauses))
        cypher.append("RETURN m")
        cypher.append("ORDER BY m.reference_time DESC, m.name")
        cypher.append("SKIP $offset")
        if limit is not None:
            cypher.append("LIMIT $limit")
            params["limit"] = limit
        records = self.find("\n".join(cypher), params)
        return [self._normalize_node(rec.get("m", rec)) for rec in records]

    def vector_search(
        self,
        query_embedding: Sequence[float],
        *,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        top_k: int = 10,
    ) -> List[GraphDriver.VectorSearchResult]:
        if top_k <= 0:
            return []
        embedding = list(query_embedding)
        if not embedding:
            return []

        cypher = (
            "WITH $embedding AS query\n"
            "MATCH (m)\n"
            "WHERE exists(m.embedding)\n"
            "  AND size(m.embedding) = size(query)\n"
            "  AND ($namespace IS NULL OR m.namespace = $namespace)\n"
            "  AND ($labels IS NULL OR m.entity_label IN $labels)\n"
            "WITH m, query,\n"
            "     reduce(dot = 0.0, idx IN range(0, size(query) - 1) |\n"
            "         dot + query[idx] * m.embedding[idx]) AS dot,\n"
            "     sqrt(reduce(sumq = 0.0, value IN query | sumq + value * value)) AS query_norm,\n"
            "     sqrt(reduce(sumn = 0.0, value IN m.embedding | sumn + value * value)) AS node_norm\n"
            "WITH m, CASE WHEN query_norm = 0 OR node_norm = 0 THEN 0.0 ELSE dot / (query_norm * node_norm) END AS score\n"
            "ORDER BY score DESC\n"
            "LIMIT $top_k\n"
            "RETURN m AS node, score"
        )
        params = {
            "embedding": embedding,
            "namespace": namespace,
            "labels": list(entity_labels) if entity_labels else None,
            "top_k": int(top_k),
        }

        records = self._run(cypher, params)
        results: List[GraphDriver.VectorSearchResult] = []
        for record in records:
            node = self._normalize_node(record.get("node"))
            try:
                score = float(record.get("score", 0.0))
            except Exception:
                score = 0.0
            results.append((node, score))
        return results

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

    def count_entities(self, namespace: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        clauses = ["($namespace IS NULL OR m.namespace = $namespace)"]
        cypher = (
            "MATCH (m)\n"
            "WHERE "
            + " AND ".join(clauses)
            + "\nRETURN coalesce(m.namespace, '') AS namespace, "
            "m.entity_label AS label, count(m) AS count"
        )
        params = {"namespace": namespace}
        rows = self.find(cypher, params)
        results: Dict[str, Dict[str, int]] = {}
        for row in rows:
            ns = row.get("namespace") or "default"
            label = row.get("label") or "Unknown"
            count = int(row.get("count", 0))
            bucket = results.setdefault(ns, {})
            bucket[label] = count
        return results

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
