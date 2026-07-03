"""Chat interface — page 4 of the loan RAG workflow."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from applications.loan_rag.constants import (
    CHAT_HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)
from applications.loan_rag.services.rag_chain import RAGConfig, RAGResult, run_rag_query
from applications.loan_rag.services.vector_store import VectorStoreResult

# Suggested questions to help new users get started
_SAMPLE_QUESTIONS = [
    "What is the minimum credit score required for a standard loan?",
    "What is the maximum debt-to-income ratio allowed?",
    "What documents are required for a self-employed applicant?",
    "What happens if a loan is overdue by 90 days?",
    "What are the interest rates for a personal loan with a score of 720?",
    "How long does a loan disbursement take after sanction?",
]


def render() -> None:
    st.header("💬 Chat with Policy")
    st.caption(
        "Ask any question about the loan policy. "
        "The LLM answers using only the retrieved policy chunks — "
        "no hallucination, every claim is traceable."
    )

    vs_result: VectorStoreResult | None = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs_result is None:
        _render_empty_state()
        return

    config: RAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, RAGConfig())
    history: list[dict] = st.session_state.setdefault(CHAT_HISTORY_SESSION_KEY, [])

    # ---- Sample questions ------------------------------------------------
    with st.expander("💡 Sample questions — click to fill", expanded=(len(history) == 0)):
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            with cols[i % 2]:
                if st.button(q, key=f"sample_{i}", use_container_width=True):
                    _run_query(q, vs_result, config, history)
                    st.rerun()

    # ---- Chat history display --------------------------------------------
    if history:
        for item in history:
            with st.chat_message("user"):
                st.write(item["query"])
            with st.chat_message("assistant"):
                st.write(item["answer"])
                with st.expander(
                    f"📎 {len(item['source_chunks'])} policy chunks used",
                    expanded=False,
                ):
                    for j, chunk in enumerate(item["source_chunks"], 1):
                        st.markdown(
                            f"<div style='font-size:.8rem;background:#f8fafc;"
                            f"border-left:3px solid #6366f1;padding:.5rem .75rem;"
                            f"border-radius:0 .4rem .4rem 0;margin-bottom:.4rem;'>"
                            f"<b>Chunk {j}</b><br>{chunk[:300].replace(chr(10), ' ')}"
                            f"{'…' if len(chunk) > 300 else ''}</div>",
                            unsafe_allow_html=True,
                        )
                st.caption(item["timestamp"])

    # ---- Input bar -------------------------------------------------------
    user_input = st.chat_input("Ask about the loan policy…")
    if user_input:
        _run_query(user_input.strip(), vs_result, config, history)
        st.rerun()

    if history:
        st.divider()
        col_clear, col_hist = st.columns([1, 3])
        with col_clear:
            if st.button("🗑 Clear chat", use_container_width=True):
                st.session_state[CHAT_HISTORY_SESSION_KEY] = []
                st.rerun()
        with col_hist:
            if st.button("→ View History", use_container_width=True):
                st.session_state[NAVIGATION_SESSION_KEY] = "📜 History"
                st.rerun()


def _run_query(
    query: str,
    vs_result: VectorStoreResult,
    config: RAGConfig,
    history: list[dict],
) -> None:
    """Execute RAG query and append result to history."""
    with st.spinner(f"Thinking with **{config.llm_model}** …"):
        try:
            result: RAGResult = run_rag_query(
                query=query,
                vectorstore=vs_result.vectorstore,
                config=config,
            )
        except Exception as exc:
            st.error(
                f"Query failed: {exc}\n\n"
                f"Make sure Ollama is running and `{config.llm_model}` is pulled."
            )
            return

    history.append({
        "query": result.query,
        "answer": result.answer,
        "source_chunks": result.source_chunks,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    })


def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("Vector store not built yet.")
        st.write("Configure RAG and build the vector store before chatting.")
        if st.button("← Go to Configure RAG", type="primary"):
            st.session_state[NAVIGATION_SESSION_KEY] = "⚙️ Configure RAG"
            st.rerun()
