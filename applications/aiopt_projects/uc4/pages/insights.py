"""UC4 — Insights: Key takeaways, interview Q&A, and connected concepts."""

import streamlit as st

from applications.aiopt_projects.uc4.constants import FALLBACK_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Streaming + Fallback")

    result = st.session_state.get(FALLBACK_RESULT_KEY)
    if result:
        st.markdown("#### Your last fallback run")
        c1, c2, c3 = st.columns(3)
        c1.metric("Model used", result.model_used)
        c2.metric("Fell back?", "Yes" if result.fell_back else "No")
        c3.metric("Attempts", result.attempts)
        st.divider()

    st.markdown("#### When to use Streaming")
    st.table({
        "Use case": [
            "Conversational chatbot",
            "Code generation assistant",
            "Document summarisation",
            "Batch API processing",
            "Email drafting tool (UI)",
        ],
        "Stream?": ["✅ Yes", "✅ Yes", "✅ Yes", "❌ No", "✅ Yes"],
        "Why": [
            "Users expect immediate feedback; streaming feels live",
            "Developers can read code as it's generated",
            "Long responses need streaming to avoid timeout",
            "No human watching — streaming adds no value",
            "Users see the draft forming, can stop early",
        ],
    })

    st.divider()
    st.markdown("#### Fallback Strategy Design")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Do**")
            st.markdown(
                "- Retry with exponential backoff (0.5s, 1s, 2s…)\n"
                "- Use a *larger* model as fallback for quality parity\n"
                "- Log every fallback event (model, error, timestamp)\n"
                "- Alert when fallback rate > 5 % (indicates primary instability)\n"
                "- Test fallback paths regularly with chaos testing"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Don't**")
            st.markdown(
                "- Retry immediately without backoff (floods the API)\n"
                "- Use the same model as fallback — it's already failing\n"
                "- Silently swallow errors without user notification\n"
                "- Set too many retries — adds too much latency before fallback\n"
                "- Forget to track fallback API cost separately"
            )

    st.divider()

    # ── Interview Q&A ────────────────────────────────────────────────────────
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions in LLM system design and production AI engineering interviews.")

    qa_pairs = [
        (
            "What is streaming in the context of LLM APIs and why does it matter for UX?",
            "Most LLM APIs support streaming via server-sent events (SSE). Instead of returning "
            "one large JSON response after the full generation, the API sends token deltas "
            "as they are produced. The client yields each delta to the UI immediately.\n\n"
            "For UX, this is critical: a 3-second response with streaming *feels* like 300 ms "
            "because the user sees the first token almost immediately. Studies show that "
            "streaming reduces perceived latency by 70–90 % versus blocking — even though "
            "the total generation time is identical."
        ),
        (
            "How do you implement streaming in Python with the Groq SDK?",
            "Set `stream=True` in `client.chat.completions.create()`. "
            "The return value is a generator. Iterate it:\n\n"
            "```python\nfor chunk in stream:\n    delta = chunk.choices[0].delta.content\n    if delta:\n        yield delta\n```\n\n"
            "In Streamlit, pass the generator to `st.write_stream()`. "
            "In FastAPI, use `StreamingResponse` with a generator that yields SSE events. "
            "In plain Python, print each delta without a newline and flush stdout."
        ),
        (
            "What is exponential backoff and why is it used in retry logic?",
            "Exponential backoff increases the wait time between retries geometrically: "
            "0.5 s → 1 s → 2 s → 4 s. This is critical for two reasons:\n\n"
            "(1) **Rate limiting**: LLM APIs return 429 when you exceed your token-per-minute "
            "quota. Retrying immediately hammers the same overloaded endpoint. Backoff gives "
            "the server time to recover and your quota to replenish.\n\n"
            "(2) **Thundering herd**: If 1000 clients all retry at exactly the same moment, "
            "the server sees a spike. Adding random jitter (e.g. ± 20 %) distributes retries "
            "across time."
        ),
        (
            "How do you design a fallback strategy for a production LLM system?",
            "A production fallback strategy has three layers:\n\n"
            "(1) **Retry layer**: 2–3 retries with exponential backoff for transient errors "
            "(429 rate limit, 503 overload). These typically resolve within seconds.\n\n"
            "(2) **Model fallback**: If all retries fail, switch to a backup model (different "
            "provider or larger/smaller model). The backup model should have a different "
            "rate-limit pool so a primary quota exhaustion doesn't also exhaust the backup.\n\n"
            "(3) **Graceful degradation**: If both primary and fallback fail, return a cached "
            "response, a static response ('Service temporarily unavailable, try again shortly'), "
            "or trigger a human escalation path. Never return a blank response."
        ),
        (
            "What metrics would you monitor in production for streaming + fallback?",
            "Key metrics:\n\n"
            "**Streaming:** Time-to-first-token (TTFT) p50/p95/p99, streaming error rate "
            "(incomplete streams), streaming abandonment rate (user leaves before completion).\n\n"
            "**Fallback:** Fallback trigger rate (% of requests that hit retry), "
            "mean time to fallback, fallback model cost vs primary model cost, "
            "error types (429 vs 503 vs timeout — different root causes).\n\n"
            "**Overall:** End-to-end success rate, mean latency, token throughput. "
            "Set alerts on fallback rate > 5 % (primary instability) and TTFT p95 > 1 s."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()

    # ── Connected Concepts ───────────────────────────────────────────────────
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("Server-Sent Events (SSE)", "The protocol that powers LLM streaming. The server sends "
         "`data: ...\\n\\n` events over an open HTTP connection. Each event contains a JSON delta. "
         "The client reads the stream and processes each event as it arrives. "
         "Supported by all major LLM APIs (OpenAI, Anthropic, Groq)."),
        ("Token Budget and Latency", "Total generation time ≈ number of output tokens × token generation speed. "
         "At 100 tokens/sec, a 500-token response takes 5 seconds. With streaming, "
         "the first token arrives in < 500 ms and the rest arrive progressively. "
         "Setting `max_tokens` limits both cost and total wait time."),
        ("Circuit Breaker Pattern", "An evolution of simple retry/fallback: if the primary model fails "
         "more than N times in a time window, 'open the circuit' and stop sending to it entirely "
         "for a cooldown period. This prevents wasting retry budget and latency on a known-down service. "
         "Libraries: `circuitbreaker` (Python), `resilience4j` (Java)."),
        ("Rate Limit Headers", "Groq and most LLM APIs return headers indicating remaining quota: "
         "`x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`, `retry-after`. "
         "Reading these headers lets you implement *proactive* rate limit management instead of "
         "reactive retry-on-429."),
        ("Graceful Degradation", "A resilience principle: when the ideal path fails, provide "
         "a degraded-but-functional response rather than a complete failure. "
         "For LLMs: return a cached answer, a simplified response from a smaller model, "
         "or a transparent error message. Never return a 500 error to an end user."),
        ("Load Balancing Across Models", "Advanced fallback: instead of a single primary and "
         "single fallback, maintain a pool of endpoints (different models, different providers). "
         "Route requests round-robin or based on health checks. "
         "This is how high-scale LLM platforms (OpenRouter, Azure OpenAI) achieve 99.9 % availability."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**You've completed AI Optimisation Techniques!** "
        "The four patterns — Semantic Caching, Model Routing, Memory Management, and Streaming + Fallback — "
        "are the foundation of production-ready LLM applications. "
        "Together they control cost, latency, context quality, and resilience."
    )
