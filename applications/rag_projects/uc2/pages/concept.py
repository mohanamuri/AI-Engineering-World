"""RAG UC2 — Concept page: Hybrid Search RAG."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Hybrid Search RAG — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why searching by meaning alone sometimes fails\n"
        "- What keyword search (BM25) is and when it wins\n"
        "- How combining two searches gives better results than either alone\n"
        "- What RRF fusion means in plain English"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem with UC1 — Meaning Search Can Miss Exact Terms")

    st.markdown(
        "UC1 searched your documents by **meaning** — great for broad questions. "
        "But what if you need to find something very specific?\n\n"
        "Imagine asking: *'What is the refund policy for order #4521-B?'*\n\n"
        "- A meaning search finds passages about *refunds in general*\n"
        "- But the exact order number **#4521-B** might never appear in those results\n"
        "- Meaning search understands concepts — it's weak on specific names, codes, and numbers"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Meaning Search alone (UC1)**")
            st.markdown(
                "✅ Great at: *'What is the cancellation policy?'*\n\n"
                "❌ Misses: *'Find clause 4.2(b)'*, *'Order #4521-B'*, *'ISO-9001 certification'*\n\n"
                "Searches by concept — exact words don't matter"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**Hybrid Search (UC2)**")
            st.markdown(
                "✅ Great at concepts *and* exact terms\n\n"
                "✅ Finds both *'cancellation policy'* and *'clause 4.2(b)'*\n\n"
                "Runs two searches, combines the best results from both"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Two Searches, One Answer")

    st.graphviz_chart("""
    digraph Hybrid {
        rankdir=TB
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        Q  [label="Your Question" fillcolor="#fce7f3" color="#ec4899"]
        S1 [label="Semantic Search\n(meaning fingerprints)" fillcolor="#dbeafe" color="#3b82f6"]
        S2 [label="BM25 Keyword Search\n(exact word matching)" fillcolor="#fef9c3" color="#eab308"]
        F  [label="RRF Fusion\n(combine & re-rank)" fillcolor="#f0fdf4" color="#22c55e"]
        A  [label="AI Writes Answer\nfrom Top Results" fillcolor="#e0f2fe" color="#0ea5e9"]

        Q -> S1
        Q -> S2
        S1 -> F
        S2 -> F
        F -> A
    }
    """)

    steps = [
        ("1️⃣ Semantic search (same as UC1)",
         "Converts your question to an embedding (fingerprint) and finds document chunks "
         "with the most similar meaning. Good at *concepts* and *paraphrases*."),
        ("2️⃣ BM25 keyword search (new in UC2)",
         "Searches for documents that contain the *exact words* from your question, "
         "ranked by how often those words appear. "
         "BM25 is like an advanced Ctrl+F — it handles typos and common words intelligently."),
        ("3️⃣ RRF Fusion — combining both results",
         "Each search returns a ranked list of chunks. "
         "RRF (Reciprocal Rank Fusion) is a scoring formula that promotes chunks "
         "appearing in *both* lists — these are clearly more relevant. "
         "The final list is re-ranked using combined scores."),
        ("4️⃣ AI writes the answer",
         "The top-ranked chunks from the fused list are passed to the AI, "
         "which writes a grounded answer. "
         "Every chunk in the answer shows *which retriever found it* — semantic or keyword."),
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
            st.markdown("**BM25**")
            st.write(
                "A keyword search algorithm. It finds documents containing your exact words "
                "and ranks them by relevance. Think of it as a smarter Ctrl+F."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Dense vs Sparse**")
            st.write(
                "Semantic search = *dense* (rich number vectors). "
                "BM25 = *sparse* (mostly zeros, one number per word). "
                "Hybrid = using both."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**RRF Fusion**")
            st.write(
                "A simple formula that combines two ranked lists. "
                "A chunk that ranks #3 in list A AND #2 in list B scores higher "
                "than one that ranks #1 in only one list."
            )

    st.success(
        "**Ready to try it?** Upload your documents and ask a question with a specific name, "
        "code, or number — then compare the retrieved sources to see which retriever found them."
    )
