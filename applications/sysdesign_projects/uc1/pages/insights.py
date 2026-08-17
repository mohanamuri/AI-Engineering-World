"""UC1 — Insights: Interview Q&A and key takeaways for Latency Budget."""

import streamlit as st

from applications.sysdesign_projects.uc1.constants import LATENCY_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Latency Budget")

    budget = st.session_state.get(LATENCY_RESULT_KEY)

    if budget:
        st.markdown("#### Your current configuration")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total latency", f"{budget.total_ms:.0f} ms")
        c2.metric("Streaming TTFT", f"{budget.total_with_streaming_ms:.0f} ms")
        c3.metric("LLM share", f"{budget.llm_pct:.1f}%")
        st.divider()

    st.markdown("#### Optimization Priority Matrix")

    st.table({
        "Component": [
            "LLM Generation",
            "LLM TTFT",
            "Streaming (no-cost)",
            "Vector Search",
            "Reranking",
            "Embedding",
            "Network",
        ],
        "Typical ms": ["800–1500", "200–400", "—", "15–50", "50–100", "10–20", "10–40"],
        "Impact": ["🔴 Very High", "🔴 High", "🟢 Free Win", "🟡 Medium", "🟡 Medium", "🟢 Low", "🟢 Low"],
        "How to reduce": [
            "Smaller model, quantization, faster hardware",
            "Warm instances, caching, provider selection",
            "Enable streaming — perceived latency = TTFT",
            "ANN indexes (HNSW), fewer retrieved chunks",
            "Remove if quality gain doesn't justify cost",
            "Smaller embedding model (384-dim vs 768-dim)",
            "CDN edge, co-locate API with vector DB",
        ],
    })

    st.divider()

    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions in ML/backend system design interviews.")

    qa_pairs = [
        (
            "What is P99 latency and why does it matter more than average latency?",
            "P99 latency is the 99th percentile: 99% of requests complete faster than this value. "
            "Average latency hides outliers — a system with average 400ms TTFT could have P99 of "
            "2,000ms if 1% of requests hit a slow path (cold start, cache miss, slow LLM call). "
            "SLAs are written in percentiles, not averages. Users who experience P99 latency are "
            "the ones who leave bad reviews. In LLM systems, common P99 culprits include: cold "
            "model instances (TTFT spike), large context windows (generation spike), and network "
            "jitter. Design your system with P99 targets, not just P50."
        ),
        (
            "How does streaming change perceived latency vs actual latency?",
            "Streaming does not change actual generation time — the model still produces the same "
            "number of tokens at the same speed. What it changes is *when the user sees output*. "
            "Without streaming: user waits ~1,600ms for the full response to appear at once. "
            "With streaming: user sees the first token after TTFT (~300ms), and the remaining text "
            "appears progressively. Perceived latency drops from 1,600ms to 300ms — an 81% "
            "improvement with zero infrastructure cost. The psychological effect is significant: "
            "users perceive a 'typing' response as fast even if total generation time is identical. "
            "Implement with `stream=True` in the LLM API call and `st.write_stream()` in Streamlit."
        ),
        (
            "How do you optimize vector search latency?",
            "Three main approaches: (1) **Index type** — use HNSW (Hierarchical Navigable Small "
            "World) graphs instead of flat search. HNSW trades ~1% recall for 100× speed at scale. "
            "All major vector DBs (Pinecone, Weaviate, Chroma) use HNSW by default. "
            "(2) **Reduce K** — retrieve fewer chunks (top-5 instead of top-20). Quality drops "
            "slightly, but latency falls proportionally. (3) **Co-location** — run your vector DB "
            "in the same VPC/region as your API. Network RTT between regions adds 20–50ms to every "
            "search call. At 30ms per search, this doubles your vector search stage latency."
        ),
        (
            "How does caching reduce latency for RAG systems?",
            "Semantic caching intercepts queries before they reach the vector search + LLM pipeline. "
            "A cache hit returns in ~5ms (embed query + cosine similarity check + return cached "
            "response) vs ~1,600ms for a full pipeline run. The effect on average latency depends "
            "on hit rate: at 30% hit rate, average latency = 0.30 × 5ms + 0.70 × 1600ms = "
            "1,121ms (30% faster). At 60% hit rate: 0.60 × 5ms + 0.40 × 1600ms = 643ms (60% "
            "faster). Beyond latency, caching also reduces LLM API costs by the same percentage. "
            "Use a semantic (embedding-based) cache rather than exact-match for natural language — "
            "otherwise the hit rate is near zero."
        ),
        (
            "How do you compare LLM providers for latency?",
            "The key metric is **tokens-per-second (tok/s)** for generation and **TTFT** for "
            "time-to-first-token. Typical benchmarks (as of 2025): Groq ~800 tok/s (fastest, "
            "LPU hardware), Together AI ~150–300 tok/s, OpenAI GPT-4o ~100 tok/s, "
            "Anthropic Claude ~80 tok/s. For a 200-token response: Groq takes ~250ms generation "
            "vs OpenAI ~2,000ms. However, speed is not the only factor — quality, reliability, "
            "pricing, and rate limits all matter. In production, measure actual P95/P99 latency "
            "under your traffic pattern, not vendor benchmarks. Use a fallback chain so a slow "
            "primary provider degrades gracefully to a faster alternative."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("TTFT vs TPOT", "TTFT = Time to First Token (user's perceived start). "
         "TPOT = Time Per Output Token (generation speed). Both matter: TTFT for perceived "
         "latency, TPOT for total response time. Target TTFT < 400ms for good UX."),
        ("Cold Start Latency", "Serverless LLM instances (Lambda, Cloud Run) take 1–5 seconds "
         "to initialize on first request. This dominates P99. Solutions: keep-warm pings, "
         "provisioned concurrency, or always-on GPU instances."),
        ("Context Window vs Latency", "Longer prompts increase both TTFT (more tokens to process "
         "in the attention mechanism) and generation cost. A 16K-token prompt is ~2–3× slower "
         "TTFT than a 2K-token prompt on the same model."),
        ("Async Processing", "For long-running requests (> 10s), switch to async: accept the "
         "request, return a job ID immediately, process in background, notify via webhook or "
         "WebSocket. This prevents HTTP timeouts and improves throughput."),
        ("Latency vs Quality Trade-offs", "Every latency optimization has a quality cost: "
         "smaller model = faster but less accurate; fewer retrieved chunks = faster but less "
         "context; no reranking = faster but lower precision. Define your SLA first, then "
         "find the highest-quality model that meets it."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC2 → Throughput & Scaling:** Now that you know your latency budget, "
        "learn how many requests per second your system can handle — and how to multiply "
        "that number with caching, batching, and horizontal scaling."
    )
