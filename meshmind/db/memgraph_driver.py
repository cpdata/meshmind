"""Memgraph implementation of GraphDriver."""
from typing import Any, Dict, List
from .base_driver import GraphDriver


"""Memgraph implementation of GraphDriver using mgclient."""
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

try:
    import mgclient
except ImportError:
    mgclient = None  # type: ignore

from .base_driver import GraphDriver


class MemgraphDriver(GraphDriver):
    """Memgraph driver implementation of GraphDriver using mgclient."""

    def __init__(self, uri: str, username: str = None, password: str = None) -> None:
        """Initialize Memgraph driver with Bolt URI and credentials."""
        if mgclient is None:
            raise ImportError("mgclient is required for MemgraphDriver")
        self.uri = uri
        self.username = username
        self.password = password
        # Parse URI: bolt://host:port
        parsed = urlparse(uri)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 7687
        # Establish connection
        self._conn = mgclient.connect(
            host=host,
            port=port,
            username=username,
            password=password,
        )
        self._cursor = self._conn.cursor()

    def _execute(self, cypher: str, params: Optional[Dict[str, Any]] = None):
        if params is None:
            params = {}
        self._cursor.execute(cypher, params)
        try:
            rows = self._cursor.fetchall()
            cols = [col[0] for col in self._cursor.description]
            results: List[Dict[str, Any]] = []
            for row in rows:
                rec: Dict[str, Any] = {}
                for idx, val in enumerate(row):
                    rec[cols[idx]] = val
                results.append(rec)
            return results
        except Exception:
            return []

    def upsert_entity(self, label: str, name: str, props: Dict[str, Any]) -> None:
        """Insert or update an entity node by uuid."""
        uid = props.get('uuid')
        cypher = (
            f"MERGE (n:{label} {{uuid: $uuid}})\n"
            f"SET n += $props"
        )
        params = {'uuid': str(uid), 'props': props}
        self._execute(cypher, params)
        self._conn.commit()

    def upsert_edge(self, subj: str, pred: str, obj: str, props: Dict[str, Any]) -> None:
        """Insert or update an edge between two entities identified by uuid."""
        cypher = (
            f"MATCH (a {{uuid: $subj}}), (b {{uuid: $obj}})\n"
            f"MERGE (a)-[r:`{pred}`]->(b)\n"
            f"SET r += $props"
        )
        params = {'subj': str(subj), 'obj': str(obj), 'props': props}
        self._execute(cypher, params)
        self._conn.commit()

    def find(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results as list of dicts."""
        return self._execute(cypher, params)

    def delete(self, uuid: Any) -> None:
        """Delete a node (and detach relationships) by uuid."""
        cypher = "MATCH (n {uuid: $uuid}) DETACH DELETE n"
        params = {'uuid': str(uuid)}
        self._execute(cypher, params)
        self._conn.commit()

    def vector_search(self, embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Fallback vector search: loads all embeddings and ranks by cosine similarity.
        """
        from meshmind.core.similarity import cosine_similarity
        # Load all entities with embeddings
        records = self.find("MATCH (n) WHERE exists(n.embedding) RETURN n.embedding AS emb, n AS node", {})
        scored = []
        for rec in records:
            emb = rec.get('emb')
            if not isinstance(emb, list):
                continue
            try:
                score = cosine_similarity(embedding, emb)
            except Exception:
                score = 0.0
            scored.append({'node': rec.get('node'), 'score': float(score)})
        # Sort and take top_k
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_k]