"""UC5 — Configure page. Tune GraphRAG parameters."""

import streamlit as st

from applications.rag_projects.services.graph_rag import GraphRAGConfig
from applications.rag_projects.uc5.constants import (
    KNOWLEDGE_GRAPH_SESSION_KEY, RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚙️ Configure GraphRAG")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    kg = st.session_state.get(KNOWLEDGE_GRAPH_SESSION_KEY)

    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return
    if kg is None:
        st.warning("Knowledge Graph not built yet. Go to **Upload Docs** and click **Build Knowledge Graph**.")
        return

    existing: GraphRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, GraphRAGConfig())

    st.write("Tune how the graph is traversed at query time. Settings take effect immediately in Chat.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Graph traversal")
        max_hops = st.slider(
            "Max traversal hops",
            min_value=1, max_value=4, value=existing.max_hops,
            help=(
                "How many relationship steps to follow from a matched entity. "
                "1 = direct neighbours only. 3 = three levels of connections. "
                "Higher hops = broader search but slower and noisier."
            ),
        )
        top_k = st.slider(
            "Max chunks to retrieve",
            min_value=2, max_value=10, value=existing.top_k,
            help="Maximum chunks gathered from graph traversal to pass to the LLM.",
        )

    with col2:
        st.markdown("#### Generation")
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=existing.temperature, step=0.05,
            help="0 = deterministic. Higher = more varied responses.",
        )
        st.markdown("#### Model")
        _models = ["llama-3.3-70b-versatile", "gemma2-9b-it", "qwen/qwen3-32b"]
        model = st.selectbox(
            "Groq LLM",
            _models,
            index=_models.index(existing.llm_model) if existing.llm_model in _models else 0,
        )

    if st.button("💾 Save Configuration", type="primary"):
        config = GraphRAGConfig(
            llm_model=model,
            top_k=top_k,
            temperature=temperature,
            max_hops=max_hops,
            max_chunks_for_graph=existing.max_chunks_for_graph,
        )
        st.session_state[RAG_CONFIG_SESSION_KEY] = config
        st.success("Configuration saved. Head to **Chat** to ask questions.")

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Entities in graph", len(kg.all_entities))
    c2.metric("Relationships", kg.edge_count)
    c3.metric("Chunks indexed", vs.chunk_count)

    st.divider()
    with st.expander("Preview knowledge graph entities", expanded=False):
        st.write("Top entities by number of chunks they appear in:")
        top_entities = sorted(
            kg.entity_chunks.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )[:15]
        for entity, chunk_ids in top_entities:
            st.markdown(f"- **{entity}** — appears in {len(chunk_ids)} chunk(s)")
