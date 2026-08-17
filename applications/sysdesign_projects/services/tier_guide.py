"""Shared Tier Guide page — shown in every System Design at Scale UC."""

import streamlit as st


def render() -> None:
    st.subheader("📋 System Design at Scale — Series Guide")

    st.markdown(
        """
        This project covers **4 essential calculators** every backend and ML engineer should understand.
        Each use case answers a real system design interview question — and all calculators are
        **pure Python with no API calls**, so you can explore them fully offline.
        """
    )

    st.divider()
    st.markdown("### The 4 Use Cases at a Glance")
    st.markdown("*Each row answers one of the most-asked system design interview questions.*")

    rows = [
        {
            "uc": "UC1",
            "technique": "Latency Budget",
            "concern": "Performance",
            "icon": "⏱️",
            "interview_q": "Where does the time go in a RAG request?",
            "one_line": "Waterfall breakdown showing network, embedding, vector search, and LLM latency at each stage.",
        },
        {
            "uc": "UC2",
            "technique": "Throughput & Scaling",
            "concern": "Scale",
            "icon": "📈",
            "interview_q": "How do you scale an LLM API from 5 RPS to 500 RPS?",
            "one_line": "Simulate how caching, batching, and horizontal replicas combine to multiply your throughput.",
        },
        {
            "uc": "UC3",
            "technique": "Architecture Patterns",
            "concern": "Design",
            "icon": "🏗️",
            "interview_q": "Which architecture should I pick for my use case?",
            "one_line": "Rule-based selector that recommends single server → load balanced → async queue → global CDN.",
        },
        {
            "uc": "UC4",
            "technique": "Cost Estimation",
            "concern": "Cost",
            "icon": "💰",
            "interview_q": "How much will this LLM system cost at scale?",
            "one_line": "Monthly projection for token costs, embeddings, infrastructure, and cache ROI.",
        },
    ]

    for r in rows:
        with st.container(border=True):
            col_badge, col_content = st.columns([1, 5])
            with col_badge:
                st.markdown(f"### {r['icon']}")
                st.markdown(f"**{r['uc']}**")
            with col_content:
                st.markdown(f"#### {r['technique']}")
                st.markdown(f"*Concern: {r['concern']}*")
                st.markdown(f"**{r['one_line']}**")
                st.caption(f"Interview question this answers: \"{r['interview_q']}\"")

    st.divider()
    st.markdown("### What Each UC Teaches — In Plain English")

    with st.expander("UC1 — Latency Budget", expanded=False):
        st.markdown(
            """
            **The problem:** "My RAG app feels slow" — but is it the embedding model? The vector DB?
            The LLM? Network? Without a breakdown, you're guessing.

            **The solution:** A latency waterfall. Break the end-to-end request into stages and measure
            each. In a typical RAG system: network ~40ms, embedding ~15ms, vector search ~30ms,
            LLM TTFT ~300ms, LLM generation ~1200ms. That's ~1600ms total — and **75–80% of it
            is the LLM**.

            **The streaming trick:** With streaming enabled, the *perceived* latency is just TTFT
            (~300ms) because the user sees the first token immediately. Total generation time is
            the same, but the experience is completely different.

            **You will learn:**
            - How to build and read a latency waterfall
            - Why LLM generation dominates total latency
            - How streaming changes perceived vs actual latency
            - P50/P95/P99 SLA targets and why P99 matters
            """
        )

    with st.expander("UC2 — Throughput & Scaling", expanded=False):
        st.markdown(
            """
            **The problem:** You benchmark at 5 RPS, and your product launches. Traffic spikes to
            50 RPS. Your system falls over. What should you have built differently?

            **The solution:** Understand the three throughput levers:
            1. **Replicas** — linear scaling (3 servers = 3× RPS), limited by cost
            2. **Caching** — serve frequent queries from cache at 5ms vs 1600ms, huge multiplier
            3. **Batching** — process 4 LLM requests in one call, amortize fixed overhead

            **You will learn:**
            - Little's Law: RPS = Concurrency / Latency
            - How a 30% cache hit rate can double your effective RPS
            - Why batching wins on GPU-based LLMs (fixed kernel launch cost)
            - The scaling curve: where adding replicas stops helping
            """
        )

    with st.expander("UC3 — Architecture Patterns", expanded=False):
        st.markdown(
            """
            **The problem:** A student asks "Should I use a load balancer or a message queue?"
            The answer is: *it depends* — on your RPS, latency budget, traffic pattern, and budget.

            **The solution:** A decision tree with 4 tiers:
            - **Single Server** — for prototypes (< 5 RPS, zero cost)
            - **Load-Balanced** — for production (10–100 RPS, stateless API replicas)
            - **Async Queue** — for burst traffic or long-running LLM jobs
            - **Global CDN** — for enterprise, multi-region, compliance (1000+ RPS)

            **You will learn:**
            - When each pattern is appropriate
            - The trade-offs: cost, complexity, latency, availability
            - How to design stateless APIs (key to horizontal scaling)
            - Where session state goes in a multi-replica system
            """
        )

    with st.expander("UC4 — Cost Estimation", expanded=False):
        st.markdown(
            """
            **The problem:** Engineering teams routinely underestimate LLM costs before launch.
            A system that costs $50/month at 1K requests/month can cost $50K/month at 1M requests.

            **The solution:** Understand the four cost buckets and model them explicitly:
            1. **LLM tokens** — input × price/1M + output × price/1M (dominant cost)
            2. **Embeddings** — cheap but recurring when docs update
            3. **Infrastructure** — vector DB, cache, hosting
            4. **Cache** — costs money but saves far more in LLM calls

            **You will learn:**
            - Token cost math from first principles
            - Cache ROI: if your cache costs $20/month and saves $200 in LLM calls, that's 10× ROI
            - Model tier selection: GPT-4o is 25× more expensive than GPT-4o mini per token
            - How to project costs at 10K, 100K, and 1M requests/month
            """
        )

    st.divider()
    st.markdown("### How These Connect: Full System Design Walkthrough")

    st.markdown(
        """
        These four calculators answer four sequential questions when designing an LLM system:

        ```
        1. LATENCY BUDGET (UC1)
           "Is my latency acceptable?" → Break it down, find the bottleneck
           ↓
        2. THROUGHPUT & SCALING (UC2)
           "Can my system handle the load?" → Calc RPS, decide on replicas + cache + batching
           ↓
        3. ARCHITECTURE PATTERN (UC3)
           "What components do I need?" → Pick the right tier (single / LB / queue / CDN)
           ↓
        4. COST ESTIMATION (UC4)
           "Can I afford this?" → Project monthly cost, find ROI on each optimization
        ```

        In an interview, walking through these four questions in order demonstrates
        **senior-level system design thinking** — you address performance, scale, architecture,
        and cost as a complete picture rather than isolated decisions.
        """
    )
