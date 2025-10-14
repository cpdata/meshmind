"""Configuration loader using environment variables."""
import os
try:
    from dotenv import load_dotenv

    # Load environment variables from .env file if present
    load_dotenv()
except ImportError:
    # python-dotenv is optional
    pass


class Settings:
    """Application settings loaded from environment variables."""

    GRAPH_BACKEND: str = os.getenv("GRAPH_BACKEND", "memory")
    MEMGRAPH_URI: str = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
    MEMGRAPH_USERNAME: str = os.getenv("MEMGRAPH_USERNAME", "")
    MEMGRAPH_PASSWORD: str = os.getenv("MEMGRAPH_PASSWORD", "")
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", ":memory:")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    REQUIRED_GROUPS = {
        "memgraph": ("MEMGRAPH_URI",),
        "neo4j": ("NEO4J_URI",),
        "openai": ("OPENAI_API_KEY",),
        "redis": ("REDIS_URL",),
    }

    def __repr__(self) -> str:
        return (
            f"Settings(GRAPH_BACKEND={self.GRAPH_BACKEND}, "
            f"MEMGRAPH_URI={self.MEMGRAPH_URI}, "
            f"MEMGRAPH_USERNAME={self.MEMGRAPH_USERNAME}, "
            f"NEO4J_URI={self.NEO4J_URI}, "
            f"REDIS_URL={self.REDIS_URL}, "
            f"EMBEDDING_MODEL={self.EMBEDDING_MODEL})"
        )

    @staticmethod
    def _mask(value: str) -> str:
        if not value:
            return ""
        if len(value) <= 4:
            return "*" * len(value)
        return f"{value[:2]}***{value[-2:]}"

    def missing(self) -> dict[str, list[str]]:
        """Return missing environment variables grouped by capability."""

        missing: dict[str, list[str]] = {}
        for group, keys in self.REQUIRED_GROUPS.items():
            if group == "memgraph" and self.GRAPH_BACKEND != "memgraph":
                continue
            if group == "neo4j" and self.GRAPH_BACKEND != "neo4j":
                continue
            absent = [key for key in keys if not getattr(self, key)]
            if absent:
                missing[group] = absent
        return missing

    def summary(self) -> dict[str, str]:
        """Return a sanitized summary of active configuration values."""

        return {
            "MEMGRAPH_URI": self.MEMGRAPH_URI,
            "MEMGRAPH_USERNAME": self.MEMGRAPH_USERNAME,
            "MEMGRAPH_PASSWORD": self._mask(self.MEMGRAPH_PASSWORD),
            "NEO4J_URI": self.NEO4J_URI,
            "NEO4J_USERNAME": self.NEO4J_USERNAME,
            "NEO4J_PASSWORD": self._mask(self.NEO4J_PASSWORD),
            "GRAPH_BACKEND": self.GRAPH_BACKEND,
            "SQLITE_PATH": self.SQLITE_PATH,
            "REDIS_URL": self.REDIS_URL,
            "OPENAI_API_KEY": self._mask(self.OPENAI_API_KEY),
            "EMBEDDING_MODEL": self.EMBEDDING_MODEL,
        }


settings = Settings()
