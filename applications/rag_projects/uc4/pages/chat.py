"""
UC4 — Chat page.

Self-RAG chat interface.
After each answer, shows a critique scorecard for every attempt:
  Groundedness · Relevance · Completeness (each 1–5)
  Pass/Fail per attempt, and which attempt produced the final answer.
"""

import streamlit as st

from applications.rag_projects.services.self_rag import (
    CritiqueRecord,
    SelfRAGConfig,
    SelfRAGResult,
    run_self_rag_query,
)
from applications.rag_projects.uc4.constants import (
    CHAT_HISTORY_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)

_SAMPLE_QUESTIONS = [
    "What is the maximum number of remote work days allowed per week?",
    "What health benefits are employees entitled to?",
    "Summarise all key rules from the code of conduct.",
    "What are the consequences of violating company policy?",
]


def render() -> None:
    st.subheader("💬 Chat")

    vs_result = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs_result is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    config: SelfRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, SelfRAGConfig())
    history: list[SelfRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    # --- Sample questions ---
    if not history:
        st.markdown("**Try a sample question:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"sample_{i}", use_container_width=True):
                _run_query(q, vs_result.vectorstore, config)
                st.rerun()
        st.divider()

    # --- Chat history ---
    for result in history:
        with st.chat_message("user"):
            st.write(result.query)
        with st.chat_message("assistant"):
            st.write(result.final_answer)
            if result.source_names:
                source_label = "  ·  ".join(f"`{s}`" for s in result.source_names)
                st.caption(f"**Sources:** {source_label}")

            final = result.critique_history[-1] if result.critique_history else None
            if final:
                passed = final.scores_ok(config.critique_threshold)
                verdict = "✅ Passed critique" if passed else f"⚠️ Best after {result.attempts} attempt(s)"
                st.caption(
                    f"{verdict}  ·  "
                    f"G:{final.groundedness} R:{final.relevance} C:{final.completeness}  ·  "
                    f"Avg: {final.avg}/5"
                )

            with st.expander("Critique scorecard", expanded=False):
                _render_scorecard(result.critique_history, config.critique_threshold)

    # --- Input ---
    query = st.chat_input("Ask a question about your documents…")
    if query:
        _run_query(query, vs_result.vectorstore, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear chat history"):
            st.session_state[CHAT_HISTORY_SESSION_KEY] = []
            st.rerun()


def _score_color(score: int, threshold: int) -> str:
    if score >= threshold:
        return "🟢"
    if score >= threshold - 1:
        return "🟡"
    return "🔴"


def _render_scorecard(history: list[CritiqueRecord], threshold: int) -> None:
    for record in history:
        passed = record.scores_ok(threshold)
        status = "✅ Passed" if passed else "❌ Failed"
        st.markdown(f"**Attempt {record.attempt}** — {status}  (avg {record.avg}/5)")

        c1, c2, c3 = st.columns(3)
        c1.metric(
            f"{_score_color(record.groundedness, threshold)} Groundedness",
            f"{record.groundedness}/5",
            delta=None,
        )
        c2.metric(
            f"{_score_color(record.relevance, threshold)} Relevance",
            f"{record.relevance}/5",
        )
        c3.metric(
            f"{_score_color(record.completeness, threshold)} Completeness",
            f"{record.completeness}/5",
        )

        if not passed and record != history[-1]:
            st.caption("Answer rewritten and re-retrieved for next attempt.")
        st.divider()


def _run_query(query: str, vectorstore, config: SelfRAGConfig) -> None:
    with st.spinner("Generating and self-critiquing answer…"):
        try:
            result = run_self_rag_query(query, vectorstore, config)
        except Exception as exc:
            st.error(f"Self-RAG failed: {exc}")
            return

    history: list[SelfRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[CHAT_HISTORY_SESSION_KEY] = history
