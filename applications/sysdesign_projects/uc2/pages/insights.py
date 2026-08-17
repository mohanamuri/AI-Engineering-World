"""UC2 — Insights: Interview Q&A and key takeaways for Throughput & Scaling."""

import streamlit as st

from applications.sysdesign_projects.uc2.constants import THROUGHPUT_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Throughput & Scaling")

    result = st.session_state.get(THROUGHPUT_RESULT_KEY)

    if result:
        st.markdown("#### Your current simulation results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Baseline RPS", f"{result.rps_no_optimisation:.2f}")
        c2.metric("Cache gain", f"+{result.cache_throughput_gain_pct:.0f}%")
        c3.metric("Batch gain", f"+{result.batch_throughput_gain_pct:.0f}%")
        c4.metric("Combined gain", f"+{result.combined_gain_pct:.0f}%")
        st.divider()

    st.markdown("#### Scaling Decision Matrix")

    st.table({
        "Strategy": [
            "Add replicas",
            "Semantic cache",
            "Request batching",
            "Faster model",
            "Async queue",
        ],
        "Best for": [
            "Predictable, sustained load",
            "Repetitive queries (FAQs, docs Q&A)",
            "High throughput, tolerable latency",
            "Latency-sensitive, cost available",
            "Bursty or long-running jobs",
        ],
        "Cost": ["High (linear)", "Low (Redis)", "Low (queue overhead)", "Medium (better API)", "Medium (queue infra)"],
        "Complexity": ["Low", "Medium", "Medium", "Low", "High"],
    })

    st.divider()

    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions in system design interviews for ML engineering roles.")

    qa_pairs = [
        (
            "What is the difference between horizontal and vertical scaling for LLM APIs?",
            "**Vertical scaling** means upgrading a single server (more RAM, faster GPU). "
            "It's simpler but has hard limits — you can only fit so much hardware in one machine — "
            "and there's no redundancy (single point of failure). "
            "**Horizontal scaling** means adding more server instances behind a load balancer. "
            "It's more complex (stateless API design required) but scales linearly and provides "
            "fault tolerance. For LLM APIs: vertical scaling helps with model inference (larger "
            "GPU = faster generation), while horizontal scaling helps with request throughput. "
            "In production, you typically do both: provision GPU instances (vertical) and run "
            "multiple (horizontal). The constraint shifts from latency to LLM API rate limits."
        ),
        (
            "How does cache hit rate affect system throughput? Show me the math.",
            "Cache hit rate directly reduces effective request latency, which increases throughput "
            "via Little's Law (RPS = N / L). Effective latency with cache: "
            "L_eff = hit_rate × cache_latency + (1 - hit_rate) × full_latency. "
            "Example: 30% hit rate, 5ms cache, 1600ms full: L_eff = 0.3×5 + 0.7×1600 = 1,121ms. "
            "Throughput gain = 1600 / 1121 = 1.43× (43% more RPS from the same hardware). "
            "At 60% hit rate: L_eff = 0.6×5 + 0.4×1600 = 643ms → 1600/643 = 2.49× gain. "
            "The relationship is nonlinear: each additional 10% hit rate is worth more than the last "
            "because you're replacing a larger fraction of expensive calls with cheap ones."
        ),
        (
            "What are the trade-offs of request batching for LLM systems?",
            "**Benefits:** On GPU hardware, the fixed cost of a forward pass (kernel launch, "
            "memory transfer) is amortized across batch_size requests. A batch-8 call might take "
            "1,650ms but serves 8 requests — 206ms effective latency vs 1600ms. This multiplies "
            "throughput by ~7.8×. **Trade-offs:** (1) Queuing latency — each request must wait "
            "for a full batch to form, adding variable latency. Bad for interactive chat where "
            "P99 latency matters. (2) Complexity — you need a queue, workers, and timeout logic "
            "(what to do with a half-full batch). (3) Batch timeout — to avoid infinite waiting, "
            "you flush partial batches after N ms. This adds a predictable latency floor. "
            "Best suited for async pipelines, document processing, and non-interactive use cases."
        ),
        (
            "When do you hit the LLM API rate limit and how do you handle it?",
            "Most LLM APIs rate-limit on **RPM** (requests per minute) and **TPM** (tokens per "
            "minute). Groq free tier: 30 RPM / 6,000 TPM. OpenAI GPT-4o: 500 RPM / 800K TPM. "
            "When your horizontal scaling produces more RPS than the API allows, all the extra "
            "replicas hit 429 errors. **Handling strategies:** (1) **Exponential backoff** — on "
            "429, wait 0.5s, 1s, 2s, 4s before retrying. (2) **Token bucket in your code** — "
            "track your own RPM counter, queue requests before they hit the limit. "
            "(3) **Multiple API keys** — distribute load across accounts (check ToS). "
            "(4) **Fallback model** — on rate limit, route to a different provider automatically. "
            "Rate limiting is why raw replica count doesn't always translate to RPS gains."
        ),
        (
            "How do you design an autoscaling policy for an LLM API service?",
            "Autoscaling for LLM APIs requires careful metric selection. CPU utilization (the "
            "default cloud metric) is often low because the bottleneck is the LLM API call, not "
            "CPU compute. Better metrics: (1) **Request queue depth** — if > 10 requests waiting, "
            "scale up. (2) **P95 latency** — if > 2s, scale up. (3) **Custom RPS metric** — "
            "track requests/replica and scale when it exceeds your target. "
            "**Scale-in (down):** be conservative. Premature scale-in causes cold starts during "
            "the next traffic spike. Keep a minimum of 2 replicas for redundancy. "
            "**Cool-down period:** LLM servers can take 30–60s to warm up (model load, index "
            "load). Set a longer scale-in delay (5 min) than scale-out delay (1 min)."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("Little's Law", "L = λW: mean number of items in a system equals arrival rate × mean wait time. "
         "Equivalently, RPS = Concurrency / Latency. Fundamental to queuing theory and capacity planning."),
        ("Amdahl's Law", "The speedup from optimization is limited by the fraction of time spent on the "
         "optimized part. If LLM generation is 80% of total latency and you make it 2× faster, "
         "total speedup = 1 / (0.2 + 0.8/2) = 1.67× — not 2×. Always fix the biggest bottleneck first."),
        ("Token Bucket Algorithm", "A rate limiting algorithm that allows bursts up to bucket size, "
         "then enforces a steady rate. Used by LLM API providers and useful in your own code to "
         "self-rate-limit before hitting API limits."),
        ("Consistent Hashing", "When you have multiple cache nodes, consistent hashing ensures that "
         "the same query always routes to the same cache node, maximizing hit rates in a distributed setup."),
        ("Circuit Breaker Pattern", "If downstream services (LLM API, vector DB) start failing, "
         "a circuit breaker 'opens' after N failures and fast-fails all requests for a timeout period. "
         "Prevents cascade failures and gives downstream services time to recover."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC3 → Architecture Patterns:** Now that you know your throughput requirements, "
        "learn which architectural pattern (single server, load balanced, async queue, CDN) "
        "fits your RPS target and budget."
    )
