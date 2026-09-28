from prometheus_client import Counter, Histogram

REQUESTS = Counter("rag_requests_total", "RAG requests", ["status"])
LATENCY = Histogram("rag_request_latency_seconds", "RAG latency")
