"""
Dynamic Groq model discovery.

Fetches available chat models from the Groq API at runtime so the app
always shows models that actually exist on the account — no more hardcoded
lists going stale when Groq decommissions models.

Usage:
    from applications.shared.groq_models import get_available_chat_models, DEFAULT_MODEL

    models = get_available_chat_models()   # ["openai/gpt-oss-20b", "openai/gpt-oss-20b", ...]
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Known fallback list (in priority order) — used if API call fails
# ---------------------------------------------------------------------------
_FALLBACK_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "compound-beta",
    "moonshotai/kimi-k2-instruct",
]

# Models to exclude from the dropdown (audio, guard, embeddings, etc.)
_EXCLUDE_KEYWORDS = ["whisper", "guard", "tts", "embed", "distil"]

DEFAULT_MODEL = _FALLBACK_MODELS[0]


def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


def get_available_chat_models() -> list[str]:
    """Return chat models available on this Groq account.

    Calls client.models.list() at runtime. Falls back to _FALLBACK_MODELS if
    the API is unreachable (e.g. running on corporate proxy from dev machine).

    Returns:
        List of model ID strings, sorted, non-empty.
    """
    try:
        from groq import Groq
        client = Groq(api_key=_get_groq_api_key())
        result = client.models.list()
        models = [
            m.id for m in result.data
            if not any(kw in m.id.lower() for kw in _EXCLUDE_KEYWORDS)
        ]
        if models:
            return sorted(models)
    except Exception:
        pass
    return list(_FALLBACK_MODELS)
