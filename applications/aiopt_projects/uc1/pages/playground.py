"""UC1 — Playground: Interactive semantic cache demo."""

import streamlit as st

from applications.aiopt_projects.services.semantic_cache import (
    CacheEntry,
    run_with_cache,
)
from applications.aiopt_projects.uc1.constants import (
    CACHE_SESSION_KEY,
    RESULT_SESSION_KEY,
    THRESHOLD_SESSION_KEY,
)


def _init() -> None:
    if CACHE_SESSION_KEY not in st.session_state:
        st.session_state[CACHE_SESSION_KEY] = []
    if THRESHOLD_SESSION_KEY not in st.session_state:
        st.session_state[THRESHOLD_SESSION_KEY] = 0.85


def render() -> None:
    st.subheader("🧪 Playground — Semantic Cache")
    _init()

    cache: list[CacheEntry] = st.session_state[CACHE_SESSION_KEY]

    # Controls
    col_t, col_c = st.columns([3, 1])
    with col_t:
        threshold = st.slider(
            "Similarity threshold",
            min_value=0.60, max_value=0.99, step=0.01,
            value=st.session_state[THRESHOLD_SESSION_KEY],
            help="Cache hit if cosine similarity ≥ threshold.",
            key=THRESHOLD_SESSION_KEY,
        )
    with col_c:
        if st.button("🗑️ Clear cache", use_container_width=True):
            st.session_state[CACHE_SESSION_KEY] = []
            st.session_state.pop(RESULT_SESSION_KEY, None)
            st.rerun()

    question = st.text_input(
        "Ask a question",
        placeholder="e.g. What is machine learning?",
    )

    if st.button("Send", type="primary", disabled=not question.strip()):
        with st.spinner("Checking cache…"):
            result, updated_cache = run_with_cache(
                question.strip(),
                cache,
                threshold=threshold,
            )
        st.session_state[CACHE_SESSION_KEY] = updated_cache
        st.session_state[RESULT_SESSION_KEY] = result
        st.rerun()

    result = st.session_state.get(RESULT_SESSION_KEY)
    if result:
        if result.cache_hit:
            st.success(f"**Cache HIT** — similarity {result.similarity:.3f} — returned in {result.latency_ms:.0f} ms (no LLM call)")
        else:
            st.info(f"**Cache MISS** — called LLM in {result.latency_ms:.0f} ms — response stored in cache")

        with st.container(border=True):
            st.markdown("**Response**")
            st.write(result.output)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cache hit?", "Yes" if result.cache_hit else "No")
        c2.metric("Similarity", f"{result.similarity:.3f}" if result.cache_hit else "—")
        c3.metric("Latency", f"{result.latency_ms:.0f} ms")
        c4.metric("Model", result.model_used)

    st.divider()
    st.markdown(f"#### Cache contents ({len(cache)} entr{'y' if len(cache) == 1 else 'ies'})")
    if not cache:
        st.caption("Cache is empty. Ask a question to populate it.")
    else:
        for i, entry in enumerate(cache, 1):
            with st.expander(f"#{i} — {entry.query[:70]}{'…' if len(entry.query) > 70 else ''}  · {entry.timestamp}"):
                st.write(entry.response[:300] + ("…" if len(entry.response) > 300 else ""))
                st.caption(f"Embedding dim: {len(entry.embedding)}")

    st.info(
        "**Try it:** Ask the same question twice — second time should be a hit. "
        "Then try a paraphrase and watch the similarity score."
    )
