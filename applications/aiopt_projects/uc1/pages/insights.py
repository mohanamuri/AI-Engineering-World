"""UC1 — Insights: Key takeaways, interview Q&A, and connected concepts."""

import streamlit as st

from applications.aiopt_projects.uc1.constants import CACHE_SESSION_KEY, RESULT_SESSION_KEY


def render() -> None:
    st.subheader("💡 Insights — Semantic Caching")

    cache = st.session_state.get(CACHE_SESSION_KEY, [])
    result = st.session_state.get(RESULT_SESSION_KEY)

    if cache or result:
        st.markdown("#### Your session stats")
        hits = sum(1 for _ in [result] if result and result.cache_hit)
        c1, c2, c3 = st.columns(3)
        c1.metric("Cache entries", len(cache))
        if result:
            c2.metric("Last call", "HIT" if result.cache_hit else "MISS")
            c3.metric("Last latency", f"{result.latency_ms:.0f} ms")
        st.divider()

    st.markdown("#### When to use Semantic Caching")
    st.table({
        "Scenario": [
            "FAQ / helpdesk chatbot",
            "Product search answers",
            "Document Q&A assistant",
            "Creative writing tool",
            "Real-time stock / news queries",
        ],
        "Cache?": ["✅ Yes", "✅ Yes", "✅ Yes", "❌ No", "❌ No"],
        "Why": [
            "Questions repeat heavily; answers are stable",
            "Product attributes rarely change",
            "Same policy questions asked repeatedly",
            "Users expect unique creative output every time",
            "Data changes by the minute — stale cache causes errors",
        ],
    })

    st.divider()
    st.markdown("#### Production Checklist")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Do**")
            st.markdown(
                "- Set threshold based on your domain (0.85 is a good default)\n"
                "- Add TTL (time-to-live) so stale answers expire\n"
                "- Log cache hit rate — aim for > 40 % in steady state\n"
                "- Use a persistent cache (Redis) across server restarts\n"
                "- Namespace caches by user or topic to avoid cross-contamination"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Don't**")
            st.markdown(
                "- Cache personalised answers (user-specific data)\n"
                "- Set threshold too low (< 0.70) — unrelated answers will match\n"
                "- Cache without TTL for time-sensitive domains\n"
                "- Use exact-match cache for natural-language queries\n"
                "- Forget to monitor cache eviction when memory fills up"
            )

    st.divider()

    # ── Interview Q&A ────────────────────────────────────────────────────────
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions asked in ML Engineering and LLM application interviews.")

    qa_pairs = [
        (
            "What is semantic caching and how does it differ from exact-match caching?",
            "Exact-match caching stores query strings as keys — it only hits if the identical "
            "string is sent again, which rarely happens in natural-language systems. Semantic "
            "caching embeds the query into a vector and uses cosine similarity to find "
            "*semantically equivalent* queries. If the similarity exceeds a threshold (e.g. 0.85), "
            "the cached response is returned without calling the LLM. This achieves 40–70 % hit "
            "rates versus near-zero for exact-match."
        ),
        (
            "How do you choose the similarity threshold for a semantic cache?",
            "Start at 0.85 — this is a safe default that prevents unrelated answers from being "
            "returned while still catching paraphrases. Tune it based on your domain: "
            "narrow domains (legal, medical) benefit from higher thresholds (0.90+) because "
            "slight wording changes can change meaning. Broad domains (general FAQs) can go lower "
            "(0.80). Monitor false-positive rates (wrong cached answer returned) and false-negative "
            "rates (missed hits that should have matched)."
        ),
        (
            "What embedding model would you choose for a production semantic cache?",
            "`all-MiniLM-L6-v2` is a strong default — 384 dimensions, ~25 MB, fast inference "
            "(< 10 ms on CPU). For higher accuracy: `all-mpnet-base-v2` (768 dim) or "
            "`text-embedding-3-small` (OpenAI, 1536 dim). Larger models give better semantic "
            "alignment but add latency. The embedding latency must be much smaller than the "
            "LLM call latency it saves — otherwise the cache provides no benefit."
        ),
        (
            "How would you handle cache invalidation in a semantic cache?",
            "Three strategies: (1) **TTL** — each entry expires after N hours/days, simple and "
            "effective for facts that change periodically. (2) **Event-driven** — invalidate "
            "entries when the underlying data changes (e.g. when a product price changes, "
            "flush all product-price cache entries). (3) **LRU eviction** — when the cache "
            "reaches a size limit, drop the least-recently-used entries. In practice, combine "
            "TTL for correctness with LRU for memory management."
        ),
        (
            "What are the risks of using a semantic cache and how do you mitigate them?",
            "Main risk: **returning a stale or slightly wrong answer** to a semantically similar "
            "but subtly different question. Mitigations: set a high threshold, add TTL, and "
            "never cache answers that involve personalisation (user account data, session state) "
            "or real-time information (stock prices, live inventory). Log and monitor cache hits "
            "with user feedback to detect drift."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()

    # ── Connected Concepts ───────────────────────────────────────────────────
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("Vector Embeddings", "Dense numerical representations of text learned by neural networks. "
         "Sentences with similar meaning cluster close together in vector space. "
         "The foundation of semantic search, RAG, and semantic caching."),
        ("Cosine Similarity", "Measures the angle between two vectors. "
         "Values near 1.0 = very similar; near 0 = unrelated; near –1 = opposite. "
         "Preferred over Euclidean distance for high-dimensional text embeddings because "
         "it's invariant to vector magnitude."),
        ("Vector Databases (Pinecone, Weaviate, ChromaDB)", "Specialised databases that store embeddings "
         "and support approximate nearest-neighbour (ANN) search at scale. In production, "
         "these replace the naive linear search used here."),
        ("Redis for Caching", "Redis supports storing JSON payloads with TTL. "
         "Combined with a vector similarity library (redis-py + RedisVL), "
         "it provides a production-grade persistent semantic cache."),
        ("Rate Limiting and Cost Control", "Semantic caching is one of three main cost-control "
         "levers in LLM systems: (1) cache → avoid calls, (2) model routing → use cheaper models, "
         "(3) prompt compression → send fewer tokens. Use all three together in production."),
        ("Cache Hit Rate", "KPI for cache effectiveness. Hit rate = hits / total requests. "
         "Typical targets: > 40 % (good), > 60 % (excellent). "
         "Low hit rate → lower threshold or seed the cache with known common queries."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC2 → Model Routing:** Even when a cache misses, you can still save cost by "
        "routing simple questions to a small fast model. Combine caching + routing for "
        "maximum efficiency."
    )
