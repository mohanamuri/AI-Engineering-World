"""Chat history page — page 5 of the HR RAG workflow."""

import streamlit as st
import json
from datetime import datetime, timezone

from applications.hr_rag.constants import CHAT_HISTORY_SESSION_KEY


def render() -> None:
    st.header("📜 History")

    history = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    if not history:
        st.info("No conversation history yet. Ask questions in the Chat page.")
        return

    st.caption(f"{len(history)} question(s) in this session.")

    for i, item in enumerate(reversed(history), 1):
        with st.expander(f"Q{len(history) - i + 1}: {item['query'][:80]}{'…' if len(item['query']) > 80 else ''}", expanded=(i == 1)):
            st.markdown(f"**Question:** {item['query']}")
            st.markdown(f"**Answer:** {item['answer']}")
            st.caption(item.get("timestamp", ""))
            st.markdown(f"*{len(item['source_chunks'])} policy chunks retrieved*")
