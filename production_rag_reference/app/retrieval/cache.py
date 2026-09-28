import hashlib
import json
import redis
from app.core.config import get_settings

class QueryCache:
    def __init__(self):
        self.redis = redis.from_url(get_settings().redis_url, decode_responses=True)
        self.ttl = get_settings().cache_ttl_seconds

    def _key(self, tenant_id, user_id, question, top_k):
        # Tenant/user MUST participate in cache identity to prevent data leakage.
        raw = f"{tenant_id}|{user_id}|{top_k}|{question.strip().lower()}"
        return "rag:answer:" + hashlib.sha256(raw.encode()).hexdigest()

    def get(self, tenant_id, user_id, question, top_k):
        value = self.redis.get(self._key(tenant_id, user_id, question, top_k))
        return json.loads(value) if value else None

    def set(self, tenant_id, user_id, question, top_k, value):
        self.redis.setex(self._key(tenant_id, user_id, question, top_k),
                         self.ttl, json.dumps(value))
