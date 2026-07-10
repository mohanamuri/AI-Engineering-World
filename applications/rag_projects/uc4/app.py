"""RAG Projects — UC4: Self-RAG (Coming Soon)."""

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
        <section class="aiew-tier-banner aiew-tb--t6">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Self-RAG</div>
                    <div class="aiew-tb-desc">
                        The model generates an answer, then critiques it on three dimensions:
                        grounded in context, relevant to the question, and complete.
                        Low scores on any dimension trigger a rewrite loop.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload → 💬 Query → ✍️ Generate → 🔍 Critique (ground · relevance · completeness) → 🔄 Rewrite if needed → ✅ Final Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Self-Reflection</span>
                        <span class="aiew-tech-pill">HuggingFace</span>
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
            <span style="color:#9a3412;font-size:.85rem;">— Final RAG use case</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### What this use case does")
        st.write(
            "UC3 (Agentic RAG) decides *when* to retrieve and *how many times*. "
            "But once a final answer is generated, neither UC1, UC2, nor UC3 ask: "
            "**is this answer actually good?**"
        )
        st.write(
            "Self-RAG adds an explicit **self-critique loop** after generation. "
            "The LLM scores its own answer on three dimensions: "
            "**Groundedness** (is every claim in the context?), "
            "**Relevance** (does the answer address the actual question?), and "
            "**Completeness** (is anything important missing?). "
            "If any score falls below a threshold, the pipeline rewrites the answer "
            "— up to a configurable maximum number of rewrite attempts."
        )

        st.markdown("### New capability over UC3")
        st.info(
            "**UC3** controls retrieval quality adaptively.\n\n"
            "**UC4** controls *generation* quality adaptively. "
            "It is the only UC where the model explicitly judges and rewrites its own output. "
            "The UI shows the critique scores and rewrite history for full transparency."
        )

    with col2:
        st.markdown("### Tech stack")
        st.table({
            "Component": [
                "Agent framework",
                "Critique mechanism",
                "Critique dimensions",
                "Rewrite strategy",
                "Embedding model",
                "LLM",
            ],
            "Technology": [
                "LangGraph StateGraph",
                "Separate LLM call scores each dimension 1–5",
                "Groundedness · Relevance · Completeness",
                "Reformulate + re-retrieve + regenerate on low scores",
                "all-MiniLM-L6-v2 (local, free)",
                "Groq llama-3.1-8b-instant",
            ],
        })

        st.markdown("### What will be built")
        st.markdown("""
- **Self-RAG graph** — LangGraph StateGraph: retrieve → generate → critique → (rewrite → retrieve → generate)* → final
- **Critique scorecard** — shows Groundedness / Relevance / Completeness scores for each generation attempt
- **Rewrite history** — every version of the answer with its critique scores, side-by-side
- **Configure page** — set critique thresholds and max rewrite attempts
- **Chat page** — final answer + expandable critique trail
        """)
