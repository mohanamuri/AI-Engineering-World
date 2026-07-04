"""Chat interface — page 4 of the HR RAG workflow."""

from __future__ import annotations
from datetime import datetime, timezone

import streamlit as st

from applications.hr_rag.constants import (
    CHAT_HISTORY_SESSION_KEY, NAVIGATION_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)
from applications.hr_rag.services.rag_chain import RAGConfig, RAGResult, run_rag_query
from applications.hr_rag.services.vector_store import VectorStoreResult

_SAMPLE_QUESTIONS = [
    "What is the company's policy on employee retention bonuses?",
    "How does the performance review process work?",
    "What are the criteria for promotion to a senior role?",
    "What flexible working arrangements are available?",
    "What is the process for raising a grievance or complaint?",
    "How is overtime compensation calculated?",
]


def render() -> None:
    st.header("💬 Chat with HR Policy")
    st.caption(
        "Ask any question about your HR policy document. "
        "Answers are grounded in the uploaded document — no hallucination."
    )

    vs_result: VectorStoreResult | None = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs_result is None:
        st.warning("Build the vector store first.")
        st.button("← Go to Configure RAG", type="primary",
                  on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: "⚙️ Configure RAG"}))
        return

    config: RAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, RAGConfig())
    history: list[dict] = st.session_state.setdefault(CHAT_HISTORY_SESSION_KEY, [])

    with st.expander("💡 Sample questions — click to ask", expanded=(len(history) == 0)):
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            with cols[i % 2]:
                if st.button(q, key=f"hr_rag_sample_{i}", use_container_width=True):
                    _run_query(q, vs_result, config, history)
                    st.rerun()

    for item in history:
        with st.chat_message("user"):
            st.write(item["query"])
        with st.chat_message("assistant"):
            st.write(item["answer"])
            with st.expander(f"📎 {len(item['source_chunks'])} policy chunks used"):
                for j, chunk in enumerate(item["source_chunks"], 1):
                    st.markdown(
                        f"<div style='font-size:.8rem;background:#f0fdf4;"
                        f"border-left:3px solid #0d9488;padding:.5rem .75rem;"
                        f"border-radius:0 .4rem .4rem 0;margin-bottom:.4rem;'>"
                        f"<b>Chunk {j}</b><br>{chunk[:300].replace(chr(10), ' ')}"
                        f"{'…' if len(chunk) > 300 else ''}</div>",
                        unsafe_allow_html=True,
                    )
            st.caption(item["timestamp"])

    user_input = st.chat_input("Ask about the HR policy…")
    if user_input:
        _run_query(user_input.strip(), vs_result, config, history)
        st.rerun()

    if history:
        col_clear, _ = st.columns([1, 3])
        with col_clear:
            if st.button("🗑 Clear chat", use_container_width=True):
                st.session_state[CHAT_HISTORY_SESSION_KEY] = []
                st.rerun()


def _run_query(query, vs_result, config, history):
    with st.spinner(f"Querying **{config.llm_model}**…"):
        try:
            result = run_rag_query(query=query, vectorstore=vs_result.vectorstore, config=config)
        except Exception as exc:
            st.error(f"Query failed: {exc}\nCheck GROQ_API_KEY.")
            return
    history.append({"query": result.query, "answer": result.answer,
                    "source_chunks": result.source_chunks,
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")})
