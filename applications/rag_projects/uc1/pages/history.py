"""
UC1 — History page.

Displays the full chat history with query, answer, and source attribution.
Useful for reviewing and comparing answers across multiple questions.
"""

import streamlit as st

from applications.rag_projects.services.rag_chain import RAGResult
from applications.rag_projects.uc1.constants import CHAT_HISTORY_SESSION_KEY


def render() -> None:
    st.subheader("📜 Chat History")

    history: list[RAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No chat history yet. Go to **Chat** to ask questions.")
        return

    st.write(f"**{len(history)} question(s)** in this session.")

    for i, result in enumerate(reversed(history), 1):
        with st.expander(f"Q{len(history) - i + 1}: {result.query[:80]}{'…' if len(result.query) > 80 else ''}", expanded=(i == 1)):
            st.markdown(f"**Question:** {result.query}")
            st.markdown(f"**Answer:**\n\n{result.answer}")

            if result.source_names:
                st.markdown("**Sources used:**")
                for name in result.source_names:
                    st.markdown(f"- `{name}`")

            st.caption(f"*{result.timestamp}*")

            with st.expander("Retrieved chunks", expanded=False):
                for j, chunk in enumerate(result.source_chunks, 1):
                    src = chunk.metadata.get("source", "unknown")
                    st.markdown(f"**Chunk {j}** — `{src}`")
                    st.text(chunk.page_content[:300] + ("…" if len(chunk.page_content) > 300 else ""))
                    if j < len(result.source_chunks):
                        st.divider()
