"""
UC3 — History page.

Full chat history with agent trace summary per question.
"""

import streamlit as st

from applications.rag_projects.services.agentic_rag import AgentRAGResult, TraceStep
from applications.rag_projects.uc3.constants import CHAT_HISTORY_SESSION_KEY

_NODE_ICON = {
    "classify": "🤔",
    "retrieve": "🔍",
    "evaluate": "📊",
    "reformulate": "✏️",
    "generate": "✅",
}


def render() -> None:
    st.subheader("📜 Chat History")

    history: list[AgentRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No chat history yet. Go to **Chat** to ask questions.")
        return

    st.write(f"**{len(history)} question(s)** in this session.")

    for i, result in enumerate(reversed(history), 1):
        label = f"Q{len(history) - i + 1}: {result.query[:80]}{'…' if len(result.query) > 80 else ''}"
        with st.expander(label, expanded=(i == 1)):
            st.markdown(f"**Question:** {result.query}")
            st.markdown(f"**Answer:**\n\n{result.answer}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Iterations", result.iterations)
            col2.metric("Agent steps", len(result.trace))
            col3.metric("Chunks used", len(result.source_chunks))

            if result.source_names:
                st.markdown("**Sources used:**")
                for name in result.source_names:
                    st.markdown(f"- `{name}`")

            st.caption(f"*{result.timestamp}*")

            with st.expander("Agent trace", expanded=False):
                for step in result.trace:
                    icon = _NODE_ICON.get(step.node, "•")
                    st.markdown(f"**{icon} {step.node.capitalize()}** — {step.message}")
                    if step.detail:
                        st.caption(step.detail)
                    st.divider()
