"""
UC5 — Chat page.

GraphRAG chat interface. After each answer shows:
- Matched entities (directly found in the graph)
- Expanded entities (discovered via BFS traversal)
- Knowledge graph subgraph (graphviz DOT)
- Source chunks with their origins
"""

import streamlit as st

from applications.rag_projects.services.graph_rag import (
    GraphRAGConfig, GraphRAGResult, graph_to_dot, run_graph_rag_query,
)
from applications.rag_projects.uc5.constants import (
    CHAT_HISTORY_SESSION_KEY,
    KNOWLEDGE_GRAPH_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)

_SAMPLE_QUESTIONS = [
    "What is the maximum number of remote work days allowed per week?",
    "What health benefits are employees entitled to?",
    "What are the consequences of violating company policy?",
    "Who is responsible for approving flexible work arrangements?",
]


def render() -> None:
    st.subheader("💬 Chat")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    kg = st.session_state.get(KNOWLEDGE_GRAPH_SESSION_KEY)

    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return
    if kg is None:
        st.warning("Knowledge Graph not built. Go to **Upload Docs** and click **Build Knowledge Graph**.")
        return

    config: GraphRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, GraphRAGConfig())
    history: list[GraphRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample question:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"g_sample_{i}", use_container_width=True):
                _run_query(q, kg, config)
                st.rerun()
        st.divider()

    for result in history:
        with st.chat_message("user"):
            st.write(result.query)
        with st.chat_message("assistant"):
            st.write(result.answer)
            if result.source_names:
                st.caption("**Sources:** " + "  ·  ".join(f"`{s}`" for s in result.source_names))

            with st.expander("Graph traversal trace", expanded=False):
                if result.matched_entities:
                    st.markdown("**Matched entities (query → graph):**")
                    st.write(", ".join(f"`{e}`" for e in result.matched_entities))
                else:
                    st.caption("No exact entity match — used first chunks as fallback.")

                if result.expanded_entities:
                    st.markdown("**Expanded entities (BFS traversal):**")
                    st.write(", ".join(f"`{e}`" for e in result.expanded_entities[:15]))

                if result.subgraph_edges:
                    st.markdown("**Traversal path (entity → relation → entity):**")
                    for e1, rel, e2 in result.subgraph_edges[:10]:
                        st.markdown(f"- `{e1}` → *{rel}* → `{e2}`")

                st.markdown(f"**Chunks retrieved via graph:** {len(result.retrieved_chunks)}")

            with st.expander("Full knowledge graph (top 20 entities)", expanded=False):
                highlight = result.matched_entities + result.expanded_entities
                dot = graph_to_dot(kg, highlight_entities=highlight)
                st.graphviz_chart(dot)

    query = st.chat_input("Ask a question about your documents…")
    if query:
        _run_query(query, kg, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear chat history"):
            st.session_state[CHAT_HISTORY_SESSION_KEY] = []
            st.rerun()


def _run_query(query: str, kg, config: GraphRAGConfig) -> None:
    with st.spinner("Traversing knowledge graph and generating answer…"):
        try:
            result = run_graph_rag_query(query, kg, config)
        except Exception as exc:
            st.error(f"GraphRAG failed: {exc}")
            return
    history: list = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[CHAT_HISTORY_SESSION_KEY] = history
