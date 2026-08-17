"""UC4 — Insights: Interview Q&A and key takeaways for Cost Estimation."""

import streamlit as st

from applications.sysdesign_projects.uc4.constants import COST_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Cost Estimation")

    breakdown = st.session_state.get(COST_RESULT_KEY)

    if breakdown:
        st.markdown("#### Your last estimate")
        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly total", f"${breakdown.total_usd:.2f}")
        c2.metric("Cost / request", f"{breakdown.cost_per_request_cents:.3f} ¢")
        c3.metric("Cache savings", f"${breakdown.savings_from_cache_usd:.2f}/month")
        st.divider()

    st.markdown("#### Cost Optimisation Priority Matrix")

    st.table({
        "Technique": [
            "Add semantic cache (30% hit rate)",
            "Switch to smaller model",
            "Prompt compression (-50% tokens)",
            "Response streaming (no cost change)",
            "Request batching",
        ],
        "Cost impact": [
            "−30% LLM cost",
            "−70–90% LLM cost",
            "−50% input token cost",
            "No cost change (UX only)",
            "No direct cost change",
        ],
        "Implementation effort": ["Medium", "Low", "Medium", "Low", "Medium"],
        "Quality impact": ["None", "Moderate", "Moderate", "None", "None"],
    })

    st.divider()

    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions in ML/backend system design interviews about cost.")

    qa_pairs = [
        (
            "How do you estimate LLM token costs before launching a product?",
            "Start with a benchmark run: take 20–50 representative user queries, run them through "
            "your full pipeline, and measure actual input + output token counts. Don't use "
            "theoretical estimates — real prompts include system message, RAG context, and "
            "conversation history which quickly inflate token counts beyond your estimate. "
            "Formula: `monthly_cost = (monthly_requests × avg_input_tokens / 1M × price_in) + "
            "(monthly_requests × avg_output_tokens / 1M × price_out)`. "
            "Assume P90 token counts, not averages — a few long conversations will dominate. "
            "Then add a 2× safety margin for growth and underestimation. "
            "For the free tier (Groq): cost is $0, but model this anyway so you know the bill "
            "when you migrate to a paid model."
        ),
        (
            "How do you calculate cache ROI and decide whether a cache is worth the cost?",
            "Cache ROI = (LLM_calls_saved × cost_per_LLM_call) / cache_monthly_cost × 100%. "
            "Example: Upstash Redis Pro = $10/month. At 50K requests/month, 30% hit rate = "
            "15K cache hits. If each LLM call costs $0.001, savings = 15K × $0.001 = $15/month. "
            "ROI = $15 / $10 = 150%. Worth it. "
            "Rule of thumb: cache pays for itself when your monthly LLM spend > $50. "
            "Below that, use in-memory cache (free) until traffic grows. "
            "Also consider latency ROI: cache hits return in 5ms vs 1600ms — even at 10% "
            "hit rate, average latency drops significantly. At high traffic, the latency "
            "and cost benefits compound."
        ),
        (
            "What are the main techniques for reducing LLM token consumption?",
            "Three categories: (1) **Prompt compression** — use a summariser to compress long "
            "conversation history, remove redundant context from RAG chunks, use bullet-point "
            "formats instead of verbose prose in system prompts. Typical saving: 30–50% of input "
            "tokens. (2) **Output length control** — add explicit length instructions ('Answer in "
            "1–2 sentences.') or use structured output (JSON with fixed schema) to prevent "
            "verbose responses. (3) **Model routing** — send simple queries to a small model "
            "(e.g. Groq free) and only send complex queries to the large model. A classifier "
            "that routes 70% of queries to the small model saves 70% × price_difference. "
            "At GPT-4o vs GPT-4o mini prices, that's ~90% cost reduction for the routed subset."
        ),
        (
            "How do you choose which model tier to use for a given task?",
            "Three-tier framework: (1) **Small (free/cheap):** factual lookup, translation, "
            "simple classification, FAQ answers where the answer is in the retrieved context. "
            "(2) **Medium:** summarization, code explanation, multi-turn conversation where "
            "reasoning spans 2–3 steps. (3) **Large:** complex reasoning, code generation, "
            "legal/medical analysis, tasks where errors are costly. "
            "Decision rule: start with the small model. If accuracy > 90% for your task in "
            "evaluation, stick with it. If not, move up one tier. "
            "Never use a large model by default — test whether you actually need it. "
            "In practice, 50–70% of LLM use cases are factual retrieval where the model's "
            "reasoning isn't the limiting factor — the retrieval quality is."
        ),
        (
            "How do you set up cost monitoring in production for an LLM system?",
            "Three layers: (1) **Provider dashboards** — OpenAI, Anthropic, Groq all provide "
            "usage dashboards. Set billing alerts at 50%, 80%, 100% of your monthly budget. "
            "(2) **Application-level logging** — log token counts per request (the API returns "
            "this in `usage.prompt_tokens` and `usage.completion_tokens`). Aggregate in "
            "Grafana/Datadog. Track P95 token count, not just average. (3) **Cost per user** "
            "— tag each request with user_id and aggregate. Identify top-10 cost users. "
            "Some users send extremely long prompts or are stuck in retry loops. "
            "Anomaly detection: alert if any single request exceeds 10K tokens (likely a bug). "
            "Alert if daily cost doubles vs trailing 7-day average."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("Token Budget Management", "For long conversations, implement a token budget: if "
         "conversation history + context + system prompt > 70% of model context window, "
         "trigger summarization. This prevents context overflow errors and controls cost."),
        ("Cost Attribution", "In multi-tenant SaaS, track LLM cost per customer. This lets you "
         "identify unprofitable customers (heavy users on low-tier plans), optimize pricing, "
         "and implement per-customer usage limits."),
        ("OpenAI Batch API", "For non-realtime tasks (bulk summarization, nightly processing), "
         "OpenAI's Batch API is 50% cheaper than the synchronous API. Requests are queued and "
         "completed within 24 hours. Significant savings at high volume."),
        ("FinOps for AI", "Financial Operations (FinOps) for AI means tracking, allocating, "
         "and optimizing cloud + API spend. Key practices: tagging all requests with "
         "cost centers, building cost forecasting models, running monthly cost reviews."),
        ("Inference Optimization", "At very high traffic, self-hosting models (vLLM, TGI) can be "
         "cheaper than API pricing. vLLM with continuous batching can serve 5–10× more tokens/second "
         "per GPU than naive inference. Break-even vs API pricing is typically > $500/month in API spend."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**You've completed all 4 use cases!** You now know how to analyse latency, "
        "model throughput, choose an architecture, and project costs. "
        "These four skills together cover the core of senior-level LLM system design."
    )
