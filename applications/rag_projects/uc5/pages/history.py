"""UC5 — History page. Full chat history with graph traversal details."""

import streamlit as st

from applications.rag_projects.services.graph_rag import GraphRAGResult
from applications.rag_projects.uc5.constants import CHAT_HISTORY_SESSION_KEY


def render() -> None:
    st.subheader("📜 Chat History")

    history: list[GraphRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No chat history yet. Go to **Chat** to ask questions.")
        return

    st.write(f"**{len(history)} question(s)** in this session.")

    for i, result in enumerate(reversed(history), 1):
        label = f"Q{len(history) - i + 1}: {result.query[:80]}{'…' if len(result.query) > 80 else ''}"
        with st.expander(label, expanded=(i == 1)):
            st.markdown(f"**Question:** {result.query}")
            st.markdown(f"**Answer:**\n\n{result.answer}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Matched entities", len(result.matched_entities))
            c2.metric("Expanded entities", len(result.expanded_entities))
            c3.metric("Chunks retrieved", len(result.retrieved_chunks))

            if result.source_names:
                st.markdown("**Sources:** " + ", ".join(f"`{s}`" for s in result.source_names))

            if result.matched_entities:
                st.markdown("**Matched:** " + ", ".join(f"`{e}`" for e in result.matched_entities))
            if result.subgraph_edges:
                st.markdown("**Traversal path:**")
                for e1, rel, e2 in result.subgraph_edges[:8]:
                    st.caption(f"  {e1} → {rel} → {e2}")

            st.caption(f"*{result.timestamp}*")
