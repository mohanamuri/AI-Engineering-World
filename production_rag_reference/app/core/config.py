from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    redis_url: str = "redis://localhost:6379/0"
    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k_dense: int = 20
    top_k_bm25: int = 20
    top_k_rerank: int = 8
    cache_ttl_seconds: int = 300
    enable_reranker: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    dev_auth_enabled: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
