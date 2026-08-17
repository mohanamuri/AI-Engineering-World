"""RAG UC7 — Concept page: Modular RAG."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Modular RAG — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why different retrieval methods find different answers\n"
        "- How Dense (vector), Sparse (BM25), and Reranker modules work\n"
        "- How Reciprocal Rank Fusion combines multiple ranked lists\n"
        "- How to compare module combinations to understand the trade-offs"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — One Retrieval Method Is Never Enough")

    st.markdown(
        "Every previous use case used one primary retrieval method (dense vector search). "
        "UC2 showed that combining dense + BM25 improved recall. "
        "But in production you often need to *experiment* — trying different combinations "
        "to see what works best for your specific documents and query patterns.\n\n"
        "**Modular RAG makes the pipeline configurable**: turn each retrieval module on or off, "
        "observe the impact, and understand the trade-off between quality and cost."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("**Module 1 — Dense**")
            st.markdown(
                "ChromaDB cosine similarity\n\n"
                "✅ Great for semantic questions\n"
                "❌ Misses exact terms/names"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**Module 2 — Sparse (BM25)**")
            st.markdown(
                "Keyword ranking\n\n"
                "✅ Great for exact terms and names\n"
                "❌ Misses paraphrase/synonym"
            )
    with col3:
        with st.container(border=True):
            st.markdown("**Module 3 — Reranker (LLM)**")
            st.markdown(
                "LLM scores each candidate 1–10\n\n"
                "✅ Highest precision\n"
                "❌ Slowest (one LLM call per chunk)"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Plug, Fuse, Answer")

    st.graphviz_chart("""
    digraph ModularRAG {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        Q  [label="Your Question" fillcolor="#fce7f3" color="#ec4899"]
        D  [label="Dense Module\n(ChromaDB)" fillcolor="#dbeafe" color="#3b82f6"]
        S  [label="Sparse Module\n(BM25)" fillcolor="#fef9c3" color="#eab308"]
        Re [label="Reranker Module\n(LLM 1-10)" fillcolor="#ede9fe" color="#7c3aed"]
        RRF [label="RRF Fusion\n(merge ranked lists)" fillcolor="#e0f2fe" color="#0ea5e9" shape=diamond]
        A  [label="Generate Answer\nwith module attribution" fillcolor="#f0fdf4" color="#22c55e"]

        Q -> D
        Q -> S
        Q -> Re
        D -> RRF
        S -> RRF
        Re -> RRF
        RRF -> A
    }
    """)

    steps = [
        ("1️⃣ Run active modules in parallel",
         "Each active module receives the question and independently returns a ranked list of chunks. "
         "Modules that are toggled off in Configure are skipped entirely."),
        ("2️⃣ Reranker scores the combined candidate pool",
         "If the Reranker is active, it receives all unique chunks from Dense + Sparse "
         "and asks the LLM: 'On a scale of 1–10, how relevant is this passage for answering the question?' "
         "This is the most expensive but most precise step."),
        ("3️⃣ Reciprocal Rank Fusion (RRF) merges results",
         "RRF is a simple formula: for each chunk, add 1/(60 + rank) for every list it appears in.\n\n"
         "A chunk ranked #1 by Dense and #1 by BM25 gets a much higher score than a chunk "
         "that appears in only one list. This rewards consistent agreement across modules.\n\n"
         "RRF is order-based — it does not care about raw similarity scores, "
         "only relative rank. This makes it robust across different scoring scales."),
        ("4️⃣ Generate answer with module attribution",
         "Every chunk in the context shows which modules contributed to its ranking "
         "(e.g., 'Dense + Sparse' or 'Reranker'). "
         "This lets you trace exactly why each passage was chosen."),
    ]
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    # ── Key terms ────────────────────────────────────────────────────────────
    st.markdown("### Key Terms (Plain English)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("**Reciprocal Rank Fusion (RRF)**")
            st.write(
                "A formula for combining ranked lists. "
                "A document gets a higher score if it consistently ranks near the top "
                "across multiple lists. Formula: score += 1/(k + rank) for each list. "
                "The k=60 constant prevents top-ranked items from dominating too much."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**BM25**")
            st.write(
                "A keyword-based ranking formula. "
                "It scores documents based on how often the search terms appear "
                "(term frequency) and how rare those terms are across all documents "
                "(inverse document frequency). Great for exact match queries."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Cross-Encoder Reranker**")
            st.write(
                "A model that reads both the query and document together to score relevance. "
                "In UC7 we use the LLM as a reranker — it receives both the question and "
                "the passage and outputs a 1–10 score. More accurate but slower than embedding."
            )

    st.success(
        "**Ready to try it?** Upload documents, then in Configure toggle different module "
        "combinations. In Chat, ask the same question with Dense-only vs all three modules "
        "and compare which chunks were selected and how the answer changed."
    )
