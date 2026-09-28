"""
Distributed tracing with LangChain callbacks.

LangChain has a built-in callback system that integrates with:
- LangSmith: LangChain's native tracing
- Custom callbacks: For logging, metrics, debugging

This module sets up callbacks for request tracking.
"""

import uuid
import time
from contextlib import contextmanager
from app.core.logging import get_logger

logger = get_logger(__name__)


def new_trace_id() -> str:
    """
    Generate a new trace ID for request correlation.

    Returns:
        UUID string for correlation across services
    """
    return str(uuid.uuid4())


@contextmanager
def Span(operation_name: str, trace_id: str):
    """
    Context manager for timing operations.

    Usage:
        with Span("retrieval", trace_id):
            results = retriever.get_relevant_documents(query)

    Args:
        operation_name: Name of the operation (retrieval, generation, etc.)
        trace_id: Correlation ID for the entire request
    """
    start = time.perf_counter()
    try:
        logger.debug("span_start", operation=operation_name, trace_id=trace_id)
        yield
    finally:
        duration = time.perf_counter() - start
        logger.info(
            "span_end",
            operation=operation_name,
            trace_id=trace_id,
            duration_seconds=duration,
        )


class RAGCallback:
    """
    Custom LangChain callback for observability.

    Logs all RAG pipeline steps (retrieval, generation) with timing.
    """

    def __init__(self, trace_id: str):
        """
        Initialize callback.

        Args:
            trace_id: Request correlation ID
        """
        self.trace_id = trace_id

    def on_retriever_start(self, serialized, input_str, **kwargs):
        """Called when retriever starts."""
        logger.debug("retriever_start", trace_id=self.trace_id, query=input_str)

    def on_retriever_end(self, documents, **kwargs):
        """Called when retriever finishes."""
        logger.debug(
            "retriever_end",
            trace_id=self.trace_id,
            num_documents=len(documents),
        )

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts."""
        logger.debug("llm_start", trace_id=self.trace_id)

    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes."""
        logger.debug("llm_end", trace_id=self.trace_id)
