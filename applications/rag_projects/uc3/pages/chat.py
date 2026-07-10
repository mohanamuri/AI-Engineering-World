"""
UC3 — Chat page.

Agentic RAG chat interface.
After each answer the agent trace is shown: every node the agent visited,
the decisions made, queries tried, context quality scores.

Node icons:
  🤔 classify   — did the agent decide retrieval was needed?
  🔍 retrieve   — which query was used, how many chunks found
  📊 evaluate   — context quality score and whether it was sufficient
  ✏️ reformulate — old query → new query
  ✅ generate   — answer produced
"""

import streamlit as st

from applications.rag_projects.services.agentic_rag import (
    AgentRAGConfig,
    AgentRAGResult,
    TraceStep,
    run_agentic_rag_query,
)
from applications.rag_projects.uc3.constants import (
    CHAT_HISTORY_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)

_NODE_ICON = {
    "classify": "🤔",
    "retrieve": "🔍",
    "evaluate": "📊",
    "reformulate": "✏️",
    "generate": "✅",
}

_SAMPLE_QUESTIONS = [
    "What is the maximum number of remote work days allowed per week?",
    "What health benefits are employees entitled to?",
    "What are the consequences of violating the code of conduct?",
    "What is 2 + 2?",   # deliberate no-retrieval test
]


def render() -> None:
    st.subheader("💬 Chat")

    vs_result = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs_result is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    config: AgentRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, AgentRAGConfig())
    history: list[AgentRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    # --- Sample questions ---
    if not history:
        st.markdown("**Try a sample question:**")
        st.caption("The last one tests whether the agent skips retrieval for a non-document question.")
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
            st.write(result.answer)
            if result.source_names:
                source_label = "  ·  ".join(f"`{s}`" for s in result.source_names)
                st.caption(f"**Sources:** {source_label}")
            st.caption(
                f"Iterations: {result.iterations}  ·  "
                f"Steps: {len(result.trace)}  ·  "
                f"Chunks used: {len(result.source_chunks)}"
            )
            with st.expander("Agent trace", expanded=False):
                _render_trace(result.trace)

    # --- Input ---
    query = st.chat_input("Ask a question about your documents…")
    if query:
        _run_query(query, vs_result.vectorstore, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear chat history"):
            st.session_state[CHAT_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_trace(trace: list[TraceStep]) -> None:
    """Render the agent's step-by-step reasoning."""
    for step in trace:
        icon = _NODE_ICON.get(step.node, "•")
        st.markdown(f"**{icon} {step.node.capitalize()}** — {step.message}")
        if step.detail:
            st.caption(step.detail)
        st.divider()


def _run_query(query: str, vectorstore, config: AgentRAGConfig) -> None:
    with st.spinner("Agent running… (classify → retrieve → evaluate → generate)"):
        try:
            result = run_agentic_rag_query(query, vectorstore, config)
        except Exception as exc:
            st.error(f"Agent failed: {exc}")
            return

    history: list[AgentRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[CHAT_HISTORY_SESSION_KEY] = history
