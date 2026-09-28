"""
Structured logging configuration.

Uses structlog for production-grade structured logging with JSON output.
All logs include trace_id for distributed tracing correlation.
"""

import structlog
from app.core.config import get_settings


def configure_logging():
    """
    Set up structlog for structured, machine-readable logging.
    All application logs should use this configured logger.
    """
    settings = get_settings()

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """
    Get a structlog logger instance.

    Example:
        logger = get_logger(__name__)
        logger.info("query_received", query="What is RAG?", user_id="user123", trace_id="trace456")
    """
    return structlog.get_logger(name)
