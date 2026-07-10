"""RAG Projects — UC3: Agentic RAG (Coming Soon)."""

import streamlit as st
from core.launcher import go_home


def run() -> None:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t5">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC3</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Agentic RAG</div>
                    <div class="aiew-tb-desc">
                        An LLM agent decides whether to retrieve, reformulates queries when
                        context is insufficient, and iterates until it has enough information
                        to answer confidently. Retrieval is no longer a fixed single step.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload → 💬 Chat → 🔄 Agent Loop (retrieve → evaluate → refine) → ✅ Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">HuggingFace</span>
                        <span class="aiew-tech-pill">ReAct</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="display:inline-flex;align-items:center;gap:.5rem;
                    background:#fff7ed;border:1px solid #fed7aa;border-radius:.5rem;
                    padding:.5rem 1rem;margin:1rem 0;">
            <span style="font-size:1.1rem;">🔧</span>
            <span style="font-weight:700;color:#c2410c;font-size:.9rem;">In Development</span>
            <span style="color:#9a3412;font-size:.85rem;">— Builds on UC2</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### What this use case does")
        st.write(
            "In UC1 and UC2 the RAG pipeline is **passive** — it always retrieves exactly once, "
            "returns the top-k chunks, and hands everything to the LLM regardless of whether "
            "the context is actually sufficient to answer the question."
        )
        st.write(
            "Agentic RAG replaces the fixed pipeline with a **LangGraph agent loop**: "
            "the agent first decides if retrieval is even needed. If it retrieves but the "
            "context is weak, it reformulates the query and retrieves again. "
            "It only generates a final answer when it is confident the context is sufficient — "
            "or after a maximum number of iterations."
        )

        st.markdown("### New capability over UC2")
        st.info(
            "**UC2** always retrieves once with a fixed query.\n\n"
            "**UC3** retrieves adaptively — zero times (if the LLM already knows), "
            "once (if context is sufficient), or multiple times with reformulated queries "
            "(if the first retrieval was weak). The agent's reasoning trace is shown in the UI."
        )

    with col2:
        st.markdown("### Tech stack")
        st.table({
            "Component": [
                "Agent framework",
                "Agent pattern",
                "Retrieval tool",
                "Query reformulation",
                "Embedding model",
                "LLM",
            ],
            "Technology": [
                "LangGraph StateGraph",
                "ReAct (Reasoning + Acting)",
                "ChromaDB similarity search (reuses UC1/UC2 vector store)",
                "Groq LLM rewrites query on low-confidence retrieval",
                "all-MiniLM-L6-v2 (local, free)",
                "Groq llama-3.1-8b-instant",
            ],
        })

        st.markdown("### What will be built")
        st.markdown("""
- **Agentic RAG graph** — LangGraph StateGraph with nodes: classify → retrieve → evaluate → (reformulate → retrieve)* → generate
- **Agent trace panel** — shows every step the agent took: which queries were tried, context quality scores, number of iterations
- **Chat page** — answers include the full reasoning trace (expandable)
- **Comparison** — side-by-side with UC1/UC2 answers to show quality improvement
        """)
