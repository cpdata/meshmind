"""In-memory implementation of :class:`GraphDriver` for tests and local development."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple
from uuid import UUID, uuid4

from meshmind.db.base_driver import GraphDriver


class InMemoryGraphDriver(GraphDriver):
    """A lightweight graph driver that stores entities and triplets in dictionaries."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._labels: Dict[str, str] = {}
        self._triplets: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_uuid(self, props: Dict[str, Any]) -> str:
        uid = props.get("uuid")
        if isinstance(uid, UUID):
            props["uuid"] = str(uid)
            return str(uid)
        if isinstance(uid, str):
            return uid
        new_uid = str(uuid4())
        props["uuid"] = new_uid
        return new_uid

    # ------------------------------------------------------------------
    # GraphDriver API
    # ------------------------------------------------------------------
    def upsert_entity(self, label: str, name: str, props: Dict[str, Any]) -> None:
        props = dict(props)
        uid = self._ensure_uuid(props)
        props.setdefault("name", name)
        props.setdefault("entity_label", label)
        self._nodes[uid] = props
        self._labels[uid] = label

    def upsert_edge(self, subj: str, pred: str, obj: str, props: Dict[str, Any]) -> None:
        key = (str(subj), pred, str(obj))
        payload = dict(props)
        payload.setdefault("subject", str(subj))
        payload.setdefault("predicate", pred)
        payload.setdefault("object", str(obj))
        self._triplets[key] = payload

    def find(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        cypher = cypher.lower().strip()
        if "where m.uuid" in cypher:
            uid = str(params.get("uuid", ""))
            node = self._nodes.get(uid)
            if node is None:
                return []
            return [{"m": dict(node)}]
        if "where m.namespace" in cypher:
            namespace = params.get("namespace")
            results = [
                {"m": dict(node)}
                for node in self._nodes.values()
                if node.get("namespace") == namespace
            ]
            return results
        if cypher.startswith("match (m) return m"):
            return [{"m": dict(node)} for node in self._nodes.values()]
        if cypher.startswith("match (a)-[r"):
            namespace = params.get("namespace")
            results: List[Dict[str, Any]] = []
            for payload in self._triplets.values():
                if namespace and payload.get("namespace") != namespace:
                    continue
                record = {
                    "subject": payload.get("subject"),
                    "predicate": payload.get("predicate"),
                    "object": payload.get("object"),
                    "namespace": payload.get("namespace"),
                    "metadata": payload.get("metadata"),
                    "reference_time": payload.get("reference_time"),
                }
                results.append(record)
            return results
        return []

    def get_entity(self, uid: str) -> Optional[Dict[str, Any]]:
        node = self._nodes.get(str(uid))
        return dict(node) if node else None

    def _filtered_nodes(
        self,
        namespace: Optional[str],
        entity_labels: Optional[Sequence[str]],
    ) -> List[Dict[str, Any]]:
        labels = set(entity_labels or [])
        results: List[Dict[str, Any]] = []
        for node in self._nodes.values():
            if namespace is not None and node.get("namespace") != namespace:
                continue
            label = node.get("entity_label") or self._labels.get(str(node.get("uuid")))
            if labels and label not in labels:
                continue
            results.append(dict(node))
        return results

    def _slice(self, items: List[Dict[str, Any]], offset: int, limit: Optional[int]) -> List[Dict[str, Any]]:
        offset = max(offset, 0)
        if limit is None:
            return items[offset:]
        if limit <= 0:
            return []
        return items[offset : offset + limit]

    def list_entities(
        self,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        nodes = self._filtered_nodes(namespace, entity_labels)
        return self._slice(nodes, offset, limit)

    def search_entities(
        self,
        query: Optional[str] = None,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        nodes = self._filtered_nodes(namespace, entity_labels)
        if query:
            needle = query.lower()
            filtered: List[Dict[str, Any]] = []
            for node in nodes:
                haystack = " ".join(
                    str(node.get(key, "")) for key in ("name", "content", "description")
                ).lower()
                metadata = node.get("metadata") or {}
                if isinstance(metadata, dict):
                    haystack += " " + " ".join(str(value).lower() for value in metadata.values())
                if needle in haystack:
                    filtered.append(node)
            nodes = filtered
        return self._slice(nodes, offset, limit)

    def delete(self, uuid: UUID) -> None:
        uid = str(uuid)
        self._nodes.pop(uid, None)
        self._labels.pop(uid, None)
        to_delete = [key for key in self._triplets if key[0] == uid or key[2] == uid]
        for key in to_delete:
            self._triplets.pop(key, None)

    def delete_triplet(self, subj: str, pred: str, obj: str) -> None:
        self._triplets.pop((str(subj), pred, str(obj)), None)

    def list_triplets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for payload in self._triplets.values():
            if namespace and payload.get("namespace") != namespace:
                continue
            results.append(
                {
                    "subject": payload.get("subject"),
                    "predicate": payload.get("predicate"),
                    "object": payload.get("object"),
                    "namespace": payload.get("namespace"),
                    "metadata": payload.get("metadata"),
                    "reference_time": payload.get("reference_time"),
                }
            )
        return results

    def count_entities(self, namespace: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        counts: Dict[str, Dict[str, int]] = {}
        for node in self._nodes.values():
            ns = node.get("namespace")
            if namespace is not None and ns != namespace:
                continue
            label = node.get("entity_label") or self._labels.get(str(node.get("uuid"))) or "Unknown"
            bucket = counts.setdefault(ns or "default", {})
            bucket[label] = bucket.get(label, 0) + 1
        return counts
