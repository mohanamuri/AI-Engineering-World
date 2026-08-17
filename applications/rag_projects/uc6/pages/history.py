"""UC6 — History page. Full chat history with CRAG grade details."""

import streamlit as st

from applications.rag_projects.services.crag import CRAGResult, RelevanceGrade, SourceDecision
from applications.rag_projects.uc6.constants import CHAT_HISTORY_SESSION_KEY

_GRADE_ICON = {
    RelevanceGrade.CORRECT: "🟢",
    RelevanceGrade.AMBIGUOUS: "🟡",
    RelevanceGrade.INCORRECT: "🔴",
}


def render() -> None:
    st.subheader("📜 Chat History")

    history: list[CRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No chat history yet. Go to **Chat** to ask questions.")
        return

    st.write(f"**{len(history)} question(s)** in this session.")

    for i, result in enumerate(reversed(history), 1):
        label = f"Q{len(history) - i + 1}: {result.query[:80]}{'…' if len(result.query) > 80 else ''}"
        with st.expander(label, expanded=(i == 1)):
            st.markdown(f"**Question:** {result.query}")
            st.markdown(f"**Source decision:** **{result.source_decision.value}**")
            st.markdown(f"**Answer:**\n\n{result.answer}")

            n_correct = sum(1 for g in result.chunk_grades if g.grade == RelevanceGrade.CORRECT)
            n_ambig = sum(1 for g in result.chunk_grades if g.grade == RelevanceGrade.AMBIGUOUS)
            n_wrong = sum(1 for g in result.chunk_grades if g.grade == RelevanceGrade.INCORRECT)
            c1, c2, c3 = st.columns(3)
            c1.metric("🟢 CORRECT", n_correct)
            c2.metric("🟡 AMBIGUOUS", n_ambig)
            c3.metric("🔴 INCORRECT", n_wrong)

            if result.wiki_passages:
                st.markdown(f"**Wikipedia articles fetched:** {len(result.wiki_passages)}")
                for wp in result.wiki_passages:
                    st.caption(f"  • {wp.title} — {wp.url}")

            if result.source_names:
                st.markdown("**Sources:** " + ", ".join(f"`{s}`" for s in result.source_names))

            st.caption(f"*{result.timestamp}*")
