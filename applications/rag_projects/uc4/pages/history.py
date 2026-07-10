"""UC4 — History page. Full chat history with critique scorecard per question."""

import streamlit as st

from applications.rag_projects.services.self_rag import CritiqueRecord, SelfRAGResult
from applications.rag_projects.uc4.constants import (
    CHAT_HISTORY_SESSION_KEY, RAG_CONFIG_SESSION_KEY,
)
from applications.rag_projects.services.self_rag import SelfRAGConfig


def render() -> None:
    st.subheader("📜 Chat History")

    history: list[SelfRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    config: SelfRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, SelfRAGConfig())

    if not history:
        st.info("No chat history yet. Go to **Chat** to ask questions.")
        return

    st.write(f"**{len(history)} question(s)** in this session.")

    for i, result in enumerate(reversed(history), 1):
        label = f"Q{len(history) - i + 1}: {result.query[:80]}{'…' if len(result.query) > 80 else ''}"
        with st.expander(label, expanded=(i == 1)):
            st.markdown(f"**Question:** {result.query}")
            st.markdown(f"**Final Answer:**\n\n{result.final_answer}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Attempts", result.attempts)
            c2.metric("Chunks used", len(result.source_chunks))
            final = result.critique_history[-1] if result.critique_history else None
            c3.metric("Final avg score", f"{final.avg}/5" if final else "—")

            if result.source_names:
                st.markdown("**Sources used:**")
                for name in result.source_names:
                    st.markdown(f"- `{name}`")

            st.caption(f"*{result.timestamp}*")

            with st.expander("Critique scorecard", expanded=False):
                for record in result.critique_history:
                    passed = record.scores_ok(config.critique_threshold)
                    st.markdown(f"**Attempt {record.attempt}** — {'✅ Passed' if passed else '❌ Failed'}  (avg {record.avg}/5)")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Groundedness", f"{record.groundedness}/5")
                    col2.metric("Relevance", f"{record.relevance}/5")
                    col3.metric("Completeness", f"{record.completeness}/5")
                    st.divider()
