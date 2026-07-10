"""UC1 — Concept: What is Semantic Caching and why it matters."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Semantic Caching")

    st.markdown(
        """
        ### The Problem: Every LLM Call Costs Money and Time

        In production, users ask overlapping questions constantly:
        - *"What is machine learning?"*
        - *"Explain machine learning to me"*
        - *"Can you define machine learning?"*

        These are **semantically identical** — same intent, same answer.
        Sending all three to the LLM wastes API cost and adds latency.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**❌ Exact-Match Cache (naïve)**")
            st.markdown(
                "Stores query text as a key. Only hits if the *exact* string matches.\n\n"
                "- *'What is ML?'* → cache miss\n"
                "- *'What is machine learning?'* → cache miss\n"
                "- *'Define ML'* → cache miss\n\n"
                "→ Cache hit rate: near 0 % in real usage."
            )

    with col2:
        with st.container(border=True):
            st.markdown("**✅ Semantic Cache**")
            st.markdown(
                "Stores query *embedding* (a vector). On each new query, "
                "compute its embedding and check cosine similarity against all cached entries.\n\n"
                "- *'What is ML?'* → 0.97 similar to cached 'What is machine learning?' → **HIT**\n"
                "- *'Define ML'* → 0.93 similar → **HIT**\n\n"
                "→ Cache hit rate: 40–70 % in production."
            )

    st.divider()
    st.markdown("### How It Works — Step by Step")

    steps = [
        ("1️⃣ Embed the query", "Pass the user's question through a sentence-transformer model (e.g. `all-MiniLM-L6-v2`). This converts text into a 384-dimensional float vector."),
        ("2️⃣ Search the cache", "Compute cosine similarity between the new embedding and every cached embedding. Find the best match."),
        ("3️⃣ Threshold check", "If `best_similarity ≥ threshold` (e.g. 0.85), it's a **cache hit** — return the stored response instantly. No LLM call."),
        ("4️⃣ Cache miss → LLM", "If no match exceeds the threshold, call the LLM, get the response, and **store** the (query, response, embedding) triple in the cache for future hits."),
    ]
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.markdown("### The Cosine Similarity Formula")
    st.latex(r"\text{similarity}(A, B) = \frac{A \cdot B}{\|A\| \cdot \|B\|}")
    st.caption(
        "Result is between –1 and 1. For sentence embeddings, values ≥ 0.85 indicate "
        "queries that are asking essentially the same thing."
    )

    st.divider()
    st.markdown("### Key Design Parameters")
    st.table({
        "Parameter": ["Embedding model", "Similarity threshold", "Cache backend", "Eviction policy"],
        "Typical choice": [
            "all-MiniLM-L6-v2 (fast, small, 384-dim)",
            "0.80–0.90 (lower = more hits, lower precision)",
            "In-memory list / Redis / Pinecone",
            "TTL (time-to-live) or LRU (least recently used)",
        ],
        "Trade-off": [
            "Larger models = better embeddings, more latency",
            "Too low → stale answers returned; too high → few hits",
            "In-memory is fast but ephemeral; Redis persists across restarts",
            "TTL works for facts that change; LRU for memory-constrained systems",
        ],
    })

    st.success(
        "**Next → Playground:** Ask questions and watch the cache fill up. "
        "Try rephrasing the same question to trigger a cache hit."
    )
