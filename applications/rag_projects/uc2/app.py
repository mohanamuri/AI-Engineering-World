"""RAG Projects — UC2: Hybrid Search RAG (Coming Soon)."""

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
        <section class="aiew-tier-banner aiew-tb--t4">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC2</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">Hybrid Search RAG</div>
                    <div class="aiew-tb-desc">
                        Combines dense vector search with sparse BM25 keyword retrieval.
                        Reciprocal Rank Fusion merges both result sets — higher recall on exact
                        terms and technical jargon that embeddings alone miss.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload Docs → ⚙️ Configure → 💬 Chat → 📊 Compare Retrievers → 📜 History</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">BM25</span>
                        <span class="aiew-tech-pill">RRF Fusion</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">HuggingFace</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ── In Development badge ─────────────────────────────────────────────────
    st.markdown(
        """
        <div style="display:inline-flex;align-items:center;gap:.5rem;
                    background:#fff7ed;border:1px solid #fed7aa;border-radius:.5rem;
                    padding:.5rem 1rem;margin:1rem 0;">
            <span style="font-size:1.1rem;">🔧</span>
            <span style="font-weight:700;color:#c2410c;font-size:.9rem;">In Development</span>
            <span style="color:#9a3412;font-size:.85rem;">— Full implementation coming next</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### What this use case does")
        st.write(
            "UC1 (Multi-Document RAG) retrieves chunks using only dense vector similarity — "
            "meaning it finds chunks that are *semantically similar* to the query. "
            "This works well for conceptual questions but struggles with exact terms: "
            "product codes, names, acronyms, or technical jargon that embeddings "
            "compress poorly."
        )
        st.write(
            "Hybrid Search RAG runs **two retrievers in parallel** on every query: "
            "a dense retriever (ChromaDB vector search) and a sparse retriever (BM25 keyword matching). "
            "The results are merged using **Reciprocal Rank Fusion (RRF)** — a rank-based "
            "algorithm that rewards chunks appearing in both result sets without needing "
            "raw scores to be on the same scale."
        )

        st.markdown("### New capability over UC1")
        st.info(
            "**UC1** retrieves by meaning only.\n\n"
            "**UC2** retrieves by meaning AND exact keywords, then fuses both rankings. "
            "A chunk about '401(k) contribution limits' that contains the exact string "
            "'23,000' will rank highly in BM25 even if its embedding is generic — "
            "something pure vector search would miss."
        )

    with col2:
        st.markdown("### Tech stack")
        st.table({
            "Component": [
                "Dense retriever",
                "Sparse retriever",
                "Fusion algorithm",
                "Embedding model",
                "LLM",
                "Vector store",
            ],
            "Technology": [
                "ChromaDB + HuggingFace all-MiniLM-L6-v2",
                "BM25 (rank_bm25 library)",
                "Reciprocal Rank Fusion (RRF, k=60)",
                "all-MiniLM-L6-v2 (local, free)",
                "Groq llama-3.1-8b-instant",
                "ChromaDB EphemeralClient (in-memory)",
            ],
        })

        st.markdown("### What will be built")
        st.markdown("""
- **Hybrid retriever service** — runs dense + BM25 in parallel, merges with RRF
- **Retriever comparison panel** — shows which chunks came from dense, BM25, or both
- **Configure page** — tune dense weight, BM25 weight, top-k per retriever
- **Chat page** — answers show source doc + which retriever found each chunk
- **History page** — full session history with retriever attribution
        """)
