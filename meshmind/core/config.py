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

    MEMGRAPH_URI: str = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
    MEMGRAPH_USERNAME: str = os.getenv("MEMGRAPH_USERNAME", "")
    MEMGRAPH_PASSWORD: str = os.getenv("MEMGRAPH_PASSWORD", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    def __repr__(self) -> str:
        return (
            f"Settings(MEMGRAPH_URI={self.MEMGRAPH_URI}, "
            f"MEMGRAPH_USERNAME={self.MEMGRAPH_USERNAME}, "
            f"REDIS_URL={self.REDIS_URL}, "
            f"EMBEDDING_MODEL={self.EMBEDDING_MODEL})"
        )


settings = Settings()