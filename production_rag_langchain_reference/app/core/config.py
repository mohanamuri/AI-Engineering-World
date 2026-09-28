"""
Core configuration management.

Loads environment variables and provides centralized settings for the RAG system.
This is the single source of truth for API keys, model names, database connections, etc.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All sensitive values (API keys) should come from .env or secrets manager.
    """

    # OpenAI configuration
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"  # Used for generation
    openai_embedding_model: str = "text-embedding-3-small"

    # LangChain tracing (optional, for LangSmith integration)
    langsmith_enabled: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "production-rag"

    # Vector store configuration
    chroma_persistence_path: str = "./chroma_db"
    chroma_collection_name: str = "rag_documents"

    # Redis configuration
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 3600  # 1 hour

    # Embedding configuration
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    embedding_batch_size: int = 32

    # RAG parameters
    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k_retrieval: int = 8

    # Security
    dev_auth_enabled: bool = True  # Demo mode; disable in production
    jwt_secret: str = "your-secret-key"  # Change in production

    # Observability
    log_level: str = "INFO"

    class Config:
        # Load from .env file
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """
    Singleton getter for application settings.
    Caches the settings instance after first load.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
