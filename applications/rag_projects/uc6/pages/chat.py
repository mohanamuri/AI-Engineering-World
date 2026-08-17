"""
UC6 — Chat page.

CRAG chat interface. After each answer shows:
- Grade for every retrieved chunk (CORRECT / AMBIGUOUS / INCORRECT + reason)
- Source decision (Local / Wikipedia / Combined)
- Wikipedia passages fetched (if any)
"""

import streamlit as st

from applications.rag_projects.services.crag import (
    CRAGConfig, CRAGResult, RelevanceGrade, SourceDecision, run_crag_query,
)
from applications.rag_projects.uc6.constants import (
    CHAT_HISTORY_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)

_SAMPLE_QUESTIONS = [
    "What is the maximum number of remote work days allowed per week?",
    "What health benefits are employees entitled to?",
    "What is the capital of France?",
    "Who invented the telephone?",
]

_GRADE_ICON = {
    RelevanceGrade.CORRECT: "🟢",
    RelevanceGrade.AMBIGUOUS: "🟡",
    RelevanceGrade.INCORRECT: "🔴",
}

_SOURCE_ICON = {
    SourceDecision.LOCAL: "📄",
    SourceDecision.WIKIPEDIA: "🌐",
    SourceDecision.COMBINED: "📄 + 🌐",
}


def render() -> None:
    st.subheader("💬 Chat")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    config: CRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, CRAGConfig())
    history: list[CRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample question:**")
        st.caption("Tip: The last two questions are *not* covered by the sample documents — watch CRAG switch to Wikipedia!")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"crag_sample_{i}", use_container_width=True):
                _run_query(q, vs, config)
                st.rerun()
        st.divider()

    for result in history:
        with st.chat_message("user"):
            st.write(result.query)
        with st.chat_message("assistant"):
            # Source decision badge
            icon = _SOURCE_ICON.get(result.source_decision, "")
            st.markdown(f"**Source: {icon} {result.source_decision.value}**")
            st.write(result.answer)
            if result.source_names:
                st.caption("**Sources:** " + "  ·  ".join(f"`{s}`" for s in result.source_names))

            with st.expander("Chunk grades", expanded=False):
                st.markdown("**Retrieved chunks and their relevance grades:**")
                for grade in result.chunk_grades:
                    icon = _GRADE_ICON.get(grade.grade, "⚪")
                    chunk = result.local_chunks[grade.chunk_idx] if grade.chunk_idx < len(result.local_chunks) else None
                    source = chunk.metadata.get("source", "unknown") if chunk else "—"
                    st.markdown(
                        f"{icon} **Chunk {grade.chunk_idx + 1}** ({source}) — "
                        f"**{grade.grade.value}**"
                    )
                    st.caption(f"Reason: {grade.reason}")

            if result.wiki_passages:
                with st.expander("Wikipedia passages fetched", expanded=False):
                    for wp in result.wiki_passages:
                        st.markdown(f"**{wp.title}** — [{wp.url}]({wp.url})")
                        st.write(wp.extract[:400] + ("…" if len(wp.extract) > 400 else ""))

    query = st.chat_input("Ask a question about your documents (or anything else)…")
    if query:
        _run_query(query, vs, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear chat history"):
            st.session_state[CHAT_HISTORY_SESSION_KEY] = []
            st.rerun()


def _run_query(query: str, vectorstore, config: CRAGConfig) -> None:
    with st.spinner("Retrieving, grading, and generating answer…"):
        try:
            result = run_crag_query(query, vectorstore, config)
        except Exception as exc:
            st.error(f"CRAG failed: {exc}")
            return
    history: list = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[CHAT_HISTORY_SESSION_KEY] = history
