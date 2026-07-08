"""
In-memory session store for the FastAPI layer.

Each upload creates a session identified by a UUID.
The session holds the intermediate artifacts (dataframe,
preprocess result, train result, eval result) that are
produced as the user walks through the ML pipeline.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd


class SessionNotFound(Exception):
    pass


@dataclass
class Session:
    dataframe: Optional[pd.DataFrame] = None
    # Column names as they appear in the original CSV (minus target + dropped cols)
    original_features: Optional[list[str]] = None
    preprocess_result: Any = None
    train_result: Any = None
    eval_result: Any = None
    explain_result: Any = None   # XAI apps (ExplainResult)


_store: dict[str, Session] = {}


def create_session() -> str:
    sid = str(uuid.uuid4())
    _store[sid] = Session()
    return sid


def get_session(session_id: str) -> Optional[Session]:
    return _store.get(session_id)


def require_session(session_id: str) -> Session:
    s = _store.get(session_id)
    if s is None:
        raise SessionNotFound(session_id)
    return s
