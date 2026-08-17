"""UC4 — Concept: Cost buckets, token math, and cache ROI explained."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Cost Estimation for LLM Systems")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- The 4 cost buckets every LLM system has (and which dominates)\n"
        "- Token cost math from first principles — input tokens × price/1M\n"
        "- How cache ROI works: spending $20/month can save $200/month in LLM calls\n"
        "- Rough benchmarks at 10K, 100K, and 1M requests/month across models\n"
        "- How to pick the right model tier based on task complexity"
    )

    st.markdown(
        "Engineering teams routinely underestimate LLM costs before launch. "
        "A system that costs $50/month at 1,000 requests/month can cost $50,000/month at 1M requests "
        "— the same system, just more traffic.\n\n"
        "Understanding the cost model before you build prevents bill shock later. "
        "More importantly, it tells you *where to invest in optimisation*: "
        "the bucket that costs the most is the one worth reducing."
    )

    st.divider()
    st.markdown("### The 4 Cost Buckets")

    buckets = [
        {
            "icon": "🤖",
            "name": "LLM Token Costs",
            "dominant": True,
            "description": (
                "Every request sends input tokens (prompt + context) and receives output tokens (generated response). "
                "You pay for both, at different rates (output is typically 2–4× more expensive per token).\n\n"
                "**Formula:** `cost = (input_tokens / 1M × price_in) + (output_tokens / 1M × price_out)`\n\n"
                "**Example:** 1,000 input + 500 output tokens, GPT-4o mini ($0.15 in / $0.60 out):\n"
                "`= (1000/1M × $0.15) + (500/1M × $0.60) = $0.00015 + $0.0003 = $0.00045 per request`\n\n"
                "At 10,000 requests/month: **$4.50/month**. At 1,000,000: **$450/month**."
            ),
        },
        {
            "icon": "📐",
            "name": "Embedding Costs",
            "dominant": False,
            "description": (
                "When you add or update documents in your knowledge base, you embed them. "
                "Typically much smaller than LLM costs because: (a) you only embed once per doc, "
                "not once per request; (b) embedding models are much cheaper than LLMs.\n\n"
                "**Options:** HuggingFace sentence-transformers = **$0** (run locally). "
                "OpenAI text-embedding-3-small = $0.02/1M tokens. "
                "For 100 docs × 2,000 tokens = 200K tokens/month → $0.004 (negligible).\n\n"
                "Embedding cost only matters at very high ingestion volume (millions of docs/month)."
            ),
        },
        {
            "icon": "🏗️",
            "name": "Infrastructure",
            "dominant": False,
            "description": (
                "Hosting, vector DB, cache, and monitoring:\n\n"
                "- **Hosting:** Render free = $0; Render paid = $7/month; AWS ECS = $20–100/month\n"
                "- **Vector DB:** ChromaDB local = $0; Pinecone starter = $70/month; Weaviate = $25+\n"
                "- **Cache (Redis):** Upstash free = $0; Upstash Pro = $10/month; ElastiCache = $15+\n\n"
                "Infrastructure is a flat monthly cost, not traffic-dependent. "
                "It dominates at low traffic and becomes negligible at high traffic."
            ),
        },
        {
            "icon": "💾",
            "name": "Cache Investment",
            "dominant": False,
            "description": (
                "Cache costs money but saves more than it costs if your hit rate is high enough.\n\n"
                "**Cache ROI formula:** `ROI = LLM_savings / cache_cost × 100%`\n\n"
                "**Example:** Cache costs $10/month (Upstash Pro Redis). "
                "30% cache hit rate on 10K requests/month = 3,000 cache hits. "
                "Each hit saves 1 LLM call worth $0.00045 → saves $1.35/month. "
                "ROI = $1.35 / $10 = 13.5% — not worth it at this traffic level!\n\n"
                "At 1M requests/month: saves $135/month → ROI = 1,350% → definitely worth it.\n\n"
                "**Rule of thumb:** Cache pays for itself when monthly LLM bill > $100."
            ),
        },
    ]

    for bucket in buckets:
        with st.container(border=True):
            badge = "🔴 Dominant cost" if bucket["dominant"] else "🟡 Secondary cost"
            st.markdown(f"### {bucket['icon']} {bucket['name']}  {badge}")
            st.markdown(bucket["description"])

    st.divider()
    st.markdown("### Cost Benchmarks by Scale")

    st.table({
        "Monthly requests": ["1,000", "10,000", "100,000", "1,000,000"],
        "Groq (free tier)": ["$0", "$0", "$0", "$0"],
        "GPT-4o mini": ["$0.45", "$4.50", "$45", "$450"],
        "GPT-4o": ["$7.50", "$75", "$750", "$7,500"],
        "Claude Sonnet": ["$9.00", "$90", "$900", "$9,000"],
    })

    st.caption(
        "Assumptions: 1,000 input tokens + 500 output tokens per request. "
        "No caching. Prices as of mid-2025 — always verify current pricing."
    )

    st.divider()
    st.markdown("### Model Tier Selection Framework")

    st.markdown(
        "Not every task needs GPT-4o. Routing by complexity saves 60–80% of LLM costs."
    )

    st.table({
        "Task type": [
            "Simple FAQ answer",
            "Code explanation",
            "Document summarisation",
            "Complex reasoning",
            "Code generation",
        ],
        "Recommended tier": [
            "Small (8B, Groq free)",
            "Small-medium",
            "Medium",
            "Large (GPT-4o, Claude Sonnet)",
            "Large",
        ],
        "Why": [
            "Factual, no nuance needed",
            "Structured, pattern-matching",
            "Extractive, not creative",
            "Multi-step inference required",
            "Correctness + edge cases matter",
        ],
        "Relative cost": ["1×", "2×", "5×", "15–25×", "15–25×"],
    })

    st.success(
        "**Next → Playground:** Set your traffic, model, and infrastructure and get an instant "
        "monthly cost projection with a pie chart breakdown and cache ROI analysis."
    )
