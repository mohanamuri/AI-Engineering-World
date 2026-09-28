"""
Query result caching with Redis.

LangChain supports semantic caching (embedding-based) and exact match caching.
This implementation uses simple exact-match caching with Redis.

Production note: LangChain's SemanticCache requires additional setup but provides
better cache hits by matching semantically similar queries.
"""

import json
import hashlib
from redis import Redis
from app.core.config import get_settings
from app.core.metrics import CACHE_HITS, CACHE_MISSES


class QueryCache:
    """
    Query result cache using Redis.

    Caches complete Q&A results: question -> (answer + citations)
    Avoids redundant retrieval and generation for repeated questions.
    """

    def __init__(self):
        """Initialize Redis connection."""
        settings = get_settings()
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = settings.cache_ttl_seconds

    def _make_key(self, tenant_id: str, user_id: str, question: str, top_k: int) -> str:
        """
        Generate a cache key from query parameters.

        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            question: Query text
            top_k: Number of results

        Returns:
            Cache key string
        """
        # Hash the question to keep key short
        question_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
        return f"rag:cache:{tenant_id}:{user_id}:{question_hash}:{top_k}"

    def get(self, tenant_id: str, user_id: str, question: str, top_k: int):
        """
        Get cached response for a query.

        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            question: Query text
            top_k: Number of results

        Returns:
            Cached response dict or None if not found
        """
        key = self._make_key(tenant_id, user_id, question, top_k)
        cached = self.redis.get(key)

        if cached:
            CACHE_HITS.inc()
            return json.loads(cached)

        CACHE_MISSES.inc()
        return None

    def set(self, tenant_id: str, user_id: str, question: str, top_k: int, response: dict):
        """
        Cache a query response.

        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            question: Query text
            top_k: Number of results
            response: Response object to cache
        """
        key = self._make_key(tenant_id, user_id, question, top_k)
        self.redis.setex(key, self.ttl, json.dumps(response))

    def clear_user_cache(self, tenant_id: str, user_id: str):
        """
        Clear all cached queries for a user.

        Use when user permissions change or documents are updated.

        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
        """
        pattern = f"rag:cache:{tenant_id}:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
