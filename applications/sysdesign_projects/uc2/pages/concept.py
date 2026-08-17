"""UC2 — Concept: Throughput, scaling, and the three RPS levers."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Throughput & Scaling")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why '5 RPS on my laptop' doesn't tell you what your system can handle in production\n"
        "- Little's Law — the fundamental equation connecting RPS, concurrency, and latency\n"
        "- Three independent levers for scaling: replicas, caching, batching\n"
        "- How each lever works, what it costs, and where it stops helping\n"
        "- Why diminishing returns hit and what to do when they do"
    )

    st.markdown(
        "You benchmark your RAG chatbot: it handles 5 requests per second. "
        "Your product launches. Traffic climbs to 15 RPS. Then 50 RPS. At 50 RPS, "
        "response times balloon to 10 seconds and errors start appearing.\n\n"
        "**Throughput** is the number of requests your system can process per second while "
        "keeping latency acceptable. Understanding throughput means understanding *why* "
        "it's bounded — and how to move those bounds."
    )

    st.divider()
    st.markdown("### Little's Law: The Fundamental Equation")

    with st.container(border=True):
        st.markdown("**Little's Law:**")
        st.latex(r"\text{Throughput (RPS)} = \frac{\text{Concurrency (N)}}{\text{Latency (L)}}")
        st.markdown(
            "If your server handles **N concurrent requests** at once, and each request takes **L seconds**, "
            "then throughput = N / L.\n\n"
            "Example: 1 replica, 1 thread, 1.6s latency → **1 / 1.6 = 0.625 RPS**\n\n"
            "To get more RPS, you must either: (a) increase N (more replicas/threads), "
            "or (b) decrease L (faster responses via caching, batching, or faster model)."
        )

    st.divider()
    st.markdown("### The Three Levers")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**🖥️ Lever 1: Replicas**")
            st.markdown(
                "Add more server instances behind a load balancer.\n\n"
                "**How it works:** 3 servers × 0.625 RPS = 1.875 RPS (linear scaling)\n\n"
                "**Limit:** Cost grows linearly with replicas. Each replica needs memory for the "
                "embedding model, ChromaDB index, etc. At some point, you're paying for servers "
                "that are mostly idle.\n\n"
                "**Typical gain:** Linear — 3× replicas = 3× RPS"
            )

    with col2:
        with st.container(border=True):
            st.markdown("**💾 Lever 2: Caching**")
            st.markdown(
                "Serve frequently-asked questions from a cache (5ms) instead of the full pipeline (1600ms).\n\n"
                "**How it works:** 30% hit rate → 30% of requests take 5ms, 70% take 1600ms. "
                "Effective latency = 0.30 × 5 + 0.70 × 1600 = 1,121ms → **43% throughput increase**.\n\n"
                "**Limit:** Hit rate depends on query distribution. Creative or personalised queries "
                "rarely repeat. Max practical hit rate ~50–60% for FAQ-style apps.\n\n"
                "**Typical gain:** 30% hit rate → ~1.4× RPS; 60% hit rate → ~3.5× RPS"
            )

    with col3:
        with st.container(border=True):
            st.markdown("**📦 Lever 3: Batching**")
            st.markdown(
                "Group multiple LLM requests into a single API call. "
                "The model processes them in parallel on GPU.\n\n"
                "**How it works:** Batch of 4 takes ~1650ms (1600 + 50ms overhead) but serves "
                "4 requests. Effective latency per request = 1650 / 4 = 412ms → **3.9× RPS**.\n\n"
                "**Limit:** Adds real latency to individual requests (each must wait for a full "
                "batch to form). Not suitable for real-time chat. Best for async pipelines.\n\n"
                "**Typical gain:** Batch-4 → ~3.7× RPS; Batch-8 → ~6× RPS"
            )

    st.divider()
    st.markdown("### Combining All Three")

    st.markdown(
        "The levers are **multiplicative** up to a point. A system with:\n"
        "- 3 replicas (3×)\n"
        "- 30% cache hit rate (~1.4×)\n"
        "- Batch size 4 (~3.7×)\n\n"
        "Can theoretically achieve: 3 × 1.4 × 3.7 = **~15× baseline RPS**.\n\n"
        "If baseline is 0.625 RPS: optimised system handles **~9.4 RPS** — from the same model "
        "and no infrastructure upgrade."
    )

    st.table({
        "Configuration": [
            "Baseline (1 replica, no opt)",
            "+ Cache (30% hit rate)",
            "+ Batching (batch=4)",
            "+ Both (cache + batch)",
            "3 replicas + cache + batch",
        ],
        "Effective RPS": ["0.63", "0.89", "2.32", "3.27", "9.81"],
        "Gain vs baseline": ["1×", "1.4×", "3.7×", "5.2×", "15.6×"],
        "Cost": ["$0", "+Redis ($10/mo)", "+Queue overhead", "+Both", "+3× server cost"],
    })

    st.divider()
    st.markdown("### Limits and Diminishing Returns")

    with st.container(border=True):
        st.markdown(
            "**When replicas stop helping:** The shared resource (vector DB, external LLM API rate limit) "
            "becomes the bottleneck. Adding more API replicas can't help if the LLM API caps you at 100 RPM.\n\n"
            "**When caching stops helping:** Query diversity is too high. Below ~15% hit rate, "
            "the cache overhead isn't worth the infrastructure cost.\n\n"
            "**When batching stops helping:** You can't fill batches. At low traffic, requests "
            "arrive too infrequently to form full batches — you're just adding latency for no throughput gain.\n\n"
            "**Amdahl's Law in LLM systems:** If the LLM API is the bottleneck and it's uncacheable "
            "and unbatchable, all other optimisations only improve the 6.2% of latency outside the LLM."
        )

    st.success(
        "**Next → Playground:** Set your latency, replicas, cache rate, and batch size "
        "with sliders and see the scaling curve update in real time."
    )
