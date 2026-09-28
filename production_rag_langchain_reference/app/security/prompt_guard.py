"""
Prompt injection prevention and query validation.

Implements defense-in-depth by sanitizing user input and validating query safety
before it reaches the LLM or retrieval stage.
"""

import re


def sanitize_user_query(question: str) -> str:
    """
    Basic sanitization of user queries.

    This is a simplified example. Production systems should use:
    - LangChain guard rails or similar
    - LLM-based detection (running query through a guard model)
    - More sophisticated pattern matching
    - Rate limiting and anomaly detection

    Args:
        question: Raw user query

    Returns:
        Sanitized query string

    Raises:
        ValueError: If query is detected as malicious
    """
    # Remove excessive whitespace
    question = " ".join(question.split())

    # Check for suspicious patterns (very basic; real systems need more)
    dangerous_patterns = [
        r"ignore.*instructions",
        r"system.*prompt",
        r"forget.*rules",
        r"override.*security",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, question, re.IGNORECASE):
            raise ValueError("Query contains suspicious patterns")

    return question


def validate_query(question: str) -> None:
    """
    Validate that a query is safe to process.

    Args:
        question: User query to validate

    Raises:
        ValueError: If query fails validation
    """
    # Length check
    if len(question.strip()) == 0:
        raise ValueError("Query cannot be empty")

    # No query should be extremely long (avoids DoS)
    if len(question) > 4000:
        raise ValueError("Query too long (max 4000 characters)")

    # Minimal validation: ensure it's mostly printable ASCII
    if not all(ord(c) < 128 or c.isspace() for c in question):
        # Could be non-ASCII; allow with caution
        pass
