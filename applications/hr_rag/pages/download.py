"""Download page — page 6 of the HR RAG workflow."""

import json
from datetime import datetime, timezone

import streamlit as st

from applications.hr_rag.constants import (
    CHAT_HISTORY_SESSION_KEY, LOAD_RESULT_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.header("⬇ Download")

    history = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    load_result = st.session_state.get(LOAD_RESULT_SESSION_KEY)

    if not history and not load_result:
        st.info("Nothing to download yet — load a document and chat first.")
        return

    if history:
        st.subheader("Export chat history")
        payload = {"exported_at": datetime.now(timezone.utc).isoformat(), "conversations": history}
        st.download_button(
            "Download chat history (.json)",
            data=json.dumps(payload, indent=2).encode(),
            file_name="hr_rag_chat_history.json",
            mime="application/json",
            use_container_width=True,
        )

        txt_lines = []
        for i, item in enumerate(history, 1):
            txt_lines.append(f"Q{i}: {item['query']}\nA{i}: {item['answer']}\n")
        st.download_button(
            "Download chat history (.txt)",
            data="\n".join(txt_lines).encode(),
            file_name="hr_rag_chat_history.txt",
            mime="text/plain",
            use_container_width=True,
        )
