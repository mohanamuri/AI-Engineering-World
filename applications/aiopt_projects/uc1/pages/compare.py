"""UC1 — Compare: Cached vs uncached latency side-by-side."""

import time

import streamlit as st

from applications.aiopt_projects.services.semantic_cache import (
    CacheEntry,
    embed,
    find_in_cache,
    run_with_cache,
)
from applications.aiopt_projects.uc1.constants import (
    CACHE_SESSION_KEY,
    THRESHOLD_SESSION_KEY,
)


def _init() -> None:
    if CACHE_SESSION_KEY not in st.session_state:
        st.session_state[CACHE_SESSION_KEY] = []
    if THRESHOLD_SESSION_KEY not in st.session_state:
        st.session_state[THRESHOLD_SESSION_KEY] = 0.85


def render() -> None:
    st.subheader("⚖️ Compare — Cached vs Uncached")
    _init()

    st.markdown(
        "Run the same question twice (or two semantically similar questions) "
        "and compare the latency saved by the semantic cache."
    )

    cache: list[CacheEntry] = st.session_state[CACHE_SESSION_KEY]
    threshold = st.session_state.get(THRESHOLD_SESSION_KEY, 0.85)

    q1 = st.text_input("Question A (will be cached after first run)", value="What is artificial intelligence?", key="aiopt_uc1_cmp_q1")
    q2 = st.text_input("Question B (paraphrase to test semantic match)", value="Define artificial intelligence", key="aiopt_uc1_cmp_q2")

    if st.button("Run both questions", type="primary"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Question A**")
            with st.spinner("Running A…"):
                res_a, cache = run_with_cache(q1.strip(), cache, threshold=threshold)
            st.session_state[CACHE_SESSION_KEY] = cache
            badge = "🟢 Cache HIT" if res_a.cache_hit else "🔵 Cache MISS (LLM called)"
            st.markdown(badge)
            st.metric("Latency", f"{res_a.latency_ms:.0f} ms")
            if res_a.cache_hit:
                st.metric("Similarity", f"{res_a.similarity:.3f}")
            with st.container(border=True):
                st.write(res_a.output[:400])

        with col2:
            st.markdown("**Question B**")
            with st.spinner("Running B…"):
                res_b, cache = run_with_cache(q2.strip(), cache, threshold=threshold)
            st.session_state[CACHE_SESSION_KEY] = cache
            badge = "🟢 Cache HIT" if res_b.cache_hit else "🔵 Cache MISS (LLM called)"
            st.markdown(badge)
            st.metric("Latency", f"{res_b.latency_ms:.0f} ms")
            if res_b.cache_hit:
                st.metric("Similarity", f"{res_b.similarity:.3f}")
            with st.container(border=True):
                st.write(res_b.output[:400])

        if res_a.cache_hit or res_b.cache_hit:
            saved = max(res_a.latency_ms, res_b.latency_ms)
            slower = min(res_a.latency_ms, res_b.latency_ms)
            if slower > 0:
                speedup = saved / slower
                st.success(
                    f"Cache delivered a **{speedup:.1f}× speedup** on the hit "
                    f"({slower:.0f} ms vs {saved:.0f} ms)."
                )

    st.divider()
    st.markdown("### Cost Analysis")
    st.markdown(
        "Every LLM call on Groq free tier costs tokens. "
        "A semantic cache converts redundant calls to pure CPU work (embedding + cosine similarity)."
    )
    st.table({
        "Scenario": ["No cache — 100 calls/day", "Cache with 50 % hit rate", "Cache with 70 % hit rate"],
        "LLM calls": [100, 50, 30],
        "Approx token cost": ["100 %", "50 %", "30 %"],
        "Avg latency": ["~800 ms", "~430 ms", "~280 ms"],
    })
