import time, uuid, structlog

def new_trace_id():
    return str(uuid.uuid4())

class Span:
    def __init__(self, name, trace_id):
        self.name, self.trace_id = name, trace_id

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        structlog.get_logger().info(
            "rag_span",
            trace_id=self.trace_id,
            span=self.name,
            latency_ms=round((time.perf_counter() - self.start) * 1000, 2),
            error=bool(exc),
        )
