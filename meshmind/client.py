"""
MeshMind client combining LLM, embedding, and graph driver.
"""
from openai import OpenAI
from typing import Any, List, Type
from meshmind.db.memgraph_driver import MemgraphDriver
from meshmind.core.config import settings


class MeshMind:
    """
    High-level client to manage extraction, preprocessing, and storage of memories.
    """
    def __init__(
        self,
        llm_client: Any = None,
        embedding_model: str | None = None,
        graph_driver: Any = None,
    ):
        # Initialize LLM client
        self.llm_client = llm_client or OpenAI()
        # Set embedding model name
        self.embedding_model = embedding_model or settings.EMBEDDING_MODEL
        # Initialize graph driver
        self.driver = graph_driver or MemgraphDriver(
            settings.MEMGRAPH_URI,
            settings.MEMGRAPH_USERNAME,
            settings.MEMGRAPH_PASSWORD,
        )

    def extract_memories(
        self,
        instructions: str,
        namespace: str,
        entity_types: List[Type[Any]],
        content: List[str],
    ) -> List[Any]:
        from meshmind.pipeline.extract import extract_memories

        return extract_memories(
            instructions=instructions,
            namespace=namespace,
            entity_types=entity_types,
            embedding_model=self.embedding_model,
            content=content,
            llm_client=self.llm_client,
        )

    def deduplicate(
        self,
        memories: List[Any],
        threshold: float = 0.95,
    ) -> List[Any]:
        from meshmind.pipeline.preprocess import deduplicate

        return deduplicate(memories, threshold)

    def score_importance(
        self,
        memories: List[Any],
    ) -> List[Any]:
        from meshmind.pipeline.preprocess import score_importance

        return score_importance(memories)

    def compress(
        self,
        memories: List[Any],
    ) -> List[Any]:
        from meshmind.pipeline.preprocess import compress

        return compress(memories)

    def store_memories(
        self,
        memories: List[Any],
    ) -> None:
        from meshmind.pipeline.store import store_memories

        store_memories(memories, self.driver)
