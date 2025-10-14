"""SQLite implementation of :class:`GraphDriver` for lightweight persistence."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from meshmind.db.base_driver import GraphDriver


class SQLiteGraphDriver(GraphDriver):
    """GraphDriver backed by SQLite tables using simple JSON columns."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self._path = str(path)
        self._conn = sqlite3.connect(self._path)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_schema(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                uuid TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                name TEXT NOT NULL,
                namespace TEXT,
                props TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS triplets (
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                namespace TEXT,
                metadata TEXT,
                reference_time TEXT,
                PRIMARY KEY (subject, predicate, object)
            )
            """
        )
        self._conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        payload = dict(row)
        if "props" in payload and payload["props"]:
            props = payload.pop("props")
            if isinstance(props, str):
                payload.update(json.loads(props))
            elif isinstance(props, dict):
                payload.update(props)
        if "metadata" in payload and isinstance(payload["metadata"], str):
            payload["metadata"] = json.loads(payload["metadata"])
        return payload

    # ------------------------------------------------------------------
    # GraphDriver API
    # ------------------------------------------------------------------
    def upsert_entity(self, label: str, name: str, props: Dict[str, Any]) -> None:
        payload = dict(props)
        uid = str(payload.get("uuid"))
        if not uid:
            raise ValueError("Memory props must include a UUID for SQLiteGraphDriver")
        payload.setdefault("entity_label", label)
        payload.setdefault("name", name)
        namespace = payload.get("namespace")
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO entities (uuid, label, name, namespace, props)
            VALUES (:uuid, :label, :name, :namespace, :props)
            ON CONFLICT(uuid) DO UPDATE SET
                label=excluded.label,
                name=excluded.name,
                namespace=excluded.namespace,
                props=excluded.props
            """,
            {
                "uuid": uid,
                "label": payload.get("entity_label", label),
                "name": payload.get("name", name),
                "namespace": namespace,
                "props": json.dumps(payload),
            },
        )
        self._conn.commit()

    def upsert_edge(self, subj: str, pred: str, obj: str, props: Dict[str, Any]) -> None:
        payload = dict(props)
        payload.setdefault("subject", subj)
        payload.setdefault("predicate", pred)
        payload.setdefault("object", obj)
        metadata = payload.get("metadata") or {}
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO triplets (subject, predicate, object, namespace, metadata, reference_time)
            VALUES (:subject, :predicate, :object, :namespace, :metadata, :reference_time)
            ON CONFLICT(subject, predicate, object) DO UPDATE SET
                namespace=excluded.namespace,
                metadata=excluded.metadata,
                reference_time=excluded.reference_time
            """,
            {
                "subject": payload["subject"],
                "predicate": payload["predicate"],
                "object": payload["object"],
                "namespace": payload.get("namespace"),
                "metadata": json.dumps(metadata),
                "reference_time": payload.get("reference_time"),
            },
        )
        self._conn.commit()

    def find(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Provide compatibility for simple MATCH queries used by MemoryManager.
        cypher_lower = cypher.lower().strip()
        cur = self._conn.cursor()
        if "where m.uuid" in cypher_lower:
            cur.execute("SELECT * FROM entities WHERE uuid = :uuid", {"uuid": params.get("uuid")})
            row = cur.fetchone()
            if not row:
                return []
            return [{"m": self._row_to_dict(row)}]
        if "where m.namespace" in cypher_lower:
            cur.execute(
                "SELECT * FROM entities WHERE namespace = :namespace",
                {"namespace": params.get("namespace")},
            )
            rows = cur.fetchall()
            return [{"m": self._row_to_dict(row)} for row in rows]
        if cypher_lower.startswith("match (m) return m"):
            cur.execute("SELECT * FROM entities")
            rows = cur.fetchall()
            return [{"m": self._row_to_dict(row)} for row in rows]
        if cypher_lower.startswith("match (a)-[r"):
            namespace = params.get("namespace")
            if namespace:
                cur.execute(
                    "SELECT * FROM triplets WHERE namespace = :namespace",
                    {"namespace": namespace},
                )
            else:
                cur.execute("SELECT * FROM triplets")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        return []

    def get_entity(self, uid: str) -> Optional[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM entities WHERE uuid = :uuid", {"uuid": uid})
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def list_entities(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        if namespace:
            cur.execute(
                "SELECT * FROM entities WHERE namespace = :namespace",
                {"namespace": namespace},
            )
        else:
            cur.execute("SELECT * FROM entities")
        rows = cur.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def delete(self, uuid: Any) -> None:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM entities WHERE uuid = :uuid", {"uuid": str(uuid)})
        cur.execute(
            "DELETE FROM triplets WHERE subject = :uuid OR object = :uuid",
            {"uuid": str(uuid)},
        )
        self._conn.commit()

    def delete_triplet(self, subj: str, pred: str, obj: str) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "DELETE FROM triplets WHERE subject = :subject AND predicate = :predicate AND object = :object",
            {"subject": str(subj), "predicate": pred, "object": str(obj)},
        )
        self._conn.commit()

    def list_triplets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        if namespace:
            cur.execute(
                "SELECT * FROM triplets WHERE namespace = :namespace",
                {"namespace": namespace},
            )
        else:
            cur.execute("SELECT * FROM triplets")
        rows = cur.fetchall()
        result = []
        for row in rows:
            payload = dict(row)
            metadata = payload.get("metadata")
            payload["metadata"] = json.loads(metadata) if metadata else {}
            result.append(payload)
        return result

    def close(self) -> None:
        self._conn.close()
