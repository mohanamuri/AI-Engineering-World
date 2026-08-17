"""Shared series-overview component for all AI Optimisation insights pages."""

import streamlit as st


def render_series_overview(current_uc: int) -> None:
    """Render the AI Optimisation Series at a Glance table.

    Args:
        current_uc: 1–4, used to highlight the current row.
    """
    st.divider()
    st.markdown("#### 📋 AI Optimisation Series at a Glance")
    st.caption(
        "Four distinct production concerns — each UC teaches one technique "
        "and answers one of the most common LLM system design interview questions."
    )

    rows = [
        (
            "UC1", "Semantic Caching", "Cost",
            '"How do you reduce LLM API costs in production?"',
            "Embed queries → cosine similarity cache → skip LLM on hit",
            current_uc == 1,
        ),
        (
            "UC2", "Model Routing", "Cost + Performance",
            '"How do you scale LLM systems without costs exploding?"',
            "Classify complexity → route simple queries to 8B, complex to 70B",
            current_uc == 2,
        ),
        (
            "UC3", "Memory Patterns", "Memory",
            '"How do LLMs maintain context across conversations?"',
            "Buffer → last N messages · Summary → compress old turns · Entity → fact store",
            current_uc == 3,
        ),
        (
            "UC4", "Streaming + Fallback", "Performance + Reliability",
            '"How do you make LLM responses feel fast? What if the API goes down?"',
            "Yield tokens as generated → perceived latency drops; retry + switch model on failure",
            current_uc == 4,
        ),
    ]

    for uc, technique, concern, interview_q, how, is_current in rows:
        prefix = "👉 " if is_current else ""
        border = True
        with st.container(border=border):
            col_uc, col_tech, col_concern = st.columns([1, 2, 2])
            col_uc.markdown(f"**{prefix}{uc}**" + (" ← *you are here*" if is_current else ""))
            col_tech.markdown(f"**{technique}**")
            col_concern.markdown(f"*{concern}*")
            st.markdown(f"**Interview Q:** {interview_q}")
            st.caption(f"How: {how}")

    st.divider()
    st.markdown("##### What each UC teaches")

    with st.expander("UC1 — Semantic Caching"):
        st.markdown(
            "- Exact-match cache → too rigid, near-zero hit rate in production\n"
            "- Semantic cache → embed the query, find nearest neighbour in vector store, "
            "return cached response if `similarity ≥ threshold`\n"
            "- Demonstrates: latency comparison (cached vs uncached), cost savings per query, cache hit rate"
        )

    with st.expander("UC2 — Model Routing"):
        st.markdown(
            "- A lightweight classifier (one 8B call, max 5 tokens) reads the query and scores its complexity\n"
            "- Simple query → `meta-llama/llama-4-scout-17b-16e-instruct` (fast, cheap)\n"
            "- Complex query → `meta-llama/llama-4-maverick-17b-128e-instruct` (slower, higher quality)\n"
            "- Demonstrates: routing decision trace, latency difference, estimated cost difference"
        )

    with st.expander("UC3 — Memory Patterns"):
        st.markdown(
            "- **Buffer Memory** → keep last N messages verbatim (simple, hits context limit)\n"
            "- **Summary Memory** → summarise old turns with LLM call, keep summary + recent (scalable)\n"
            "- **Entity Memory** → extract named entities each turn, build a persistent fact store\n"
            "- Demonstrates: side-by-side comparison of all 3 on a multi-turn conversation"
        )

    with st.expander("UC4 — Streaming + Fallback"):
        st.markdown(
            "- **Streaming**: tokens appear as generated → perceived latency drops 70–90 %\n"
            "- **Fallback**: primary model fails or rate-limits → "
            "automatic retry with exponential backoff → switch to fallback model\n"
            "- Demonstrates: streaming vs blocking side-by-side, fallback trigger demo"
        )
