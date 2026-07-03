"""Chat history — page 5 of the loan RAG workflow."""

from __future__ import annotations

import streamlit as st

from applications.loan_rag.constants import (
    CHAT_HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
)


def render() -> None:
    st.header("📜 Chat History")
    st.caption("All Q&A pairs from this session. Export them from the Download page.")

    history: list[dict] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        with st.container(border=True):
            st.info("No chat history yet.")
            st.button(
                "← Go to Chat",
                type="primary",
                on_click=lambda: st.session_state.update(
                    {NAVIGATION_SESSION_KEY: "💬 Chat"}
                ),
            )
        return

    # ---- Stats -----------------------------------------------------------
    m1, m2 = st.columns(2)
    m1.metric("Total questions asked", len(history))
    avg_chunks = sum(len(h["source_chunks"]) for h in history) / len(history)
    m2.metric("Avg chunks retrieved", f"{avg_chunks:.1f}")

    st.divider()

    # ---- History table ---------------------------------------------------
    for i, item in enumerate(reversed(history), 1):
        with st.container(border=True):
            col_num, col_content = st.columns([1, 11])
            with col_num:
                st.markdown(
                    f"<div style='font-size:1.1rem;font-weight:700;"
                    f"color:#6366f1;padding-top:.3rem;'>{len(history) - i + 1}</div>",
                    unsafe_allow_html=True,
                )
            with col_content:
                st.markdown(f"**Q:** {item['query']}")
                st.markdown(f"**A:** {item['answer']}")
                st.caption(
                    f"{item['timestamp']} · {len(item['source_chunks'])} chunks retrieved"
                )

    st.divider()
    col_chat, col_dl = st.columns(2)
    with col_chat:
        st.button(
            "← Back to Chat",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "💬 Chat"}
            ),
        )
    with col_dl:
        st.button(
            "→ Download History",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "⬇ Download"}
            ),
        )
