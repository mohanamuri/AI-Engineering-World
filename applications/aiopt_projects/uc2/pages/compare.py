"""UC2 — Compare: Routed model vs fixed model side-by-side."""

import streamlit as st

from applications.aiopt_projects.services.model_router import (
    LARGE_MODEL,
    SMALL_MODEL,
    run_fixed_model,
    run_routed,
)


COMPARISON_QUERIES = [
    "What is the capital of Japan?",
    "Explain the difference between supervised and unsupervised learning",
    "Write a Python class that implements a thread-safe queue with a max size limit, "
    "blocking put/get, and a timeout parameter.",
]


def render() -> None:
    st.subheader("⚖️ Compare — Routed vs Fixed Model")

    st.markdown(
        "Run the same query three ways — routed (smart), always-small (cheap), always-large (expensive) "
        "— and compare quality, latency, and cost."
    )

    query = st.selectbox(
        "Choose a test query",
        options=COMPARISON_QUERIES,
        key="aiopt_uc2_cmp_query",
    )
    custom = st.text_area("Or enter your own:", key="aiopt_uc2_cmp_custom", height=80)
    final_query = custom.strip() if custom.strip() else query

    if st.button("Run all three", type="primary"):
        col_r, col_s, col_l = st.columns(3)

        with col_r:
            st.markdown("**🔀 Routed**")
            with st.spinner("Routing…"):
                routed = run_routed(final_query)
            st.metric("Model selected", routed.routing.model_selected.split("-")[1] if "-" in routed.routing.model_selected else routed.routing.model_selected)
            st.metric("Complexity", routed.routing.complexity)
            st.metric("Total latency", f"{routed.total_latency_ms:.0f} ms")
            st.metric("Tokens out", routed.tokens_out)
            with st.container(border=True):
                st.write(routed.output[:500])

        with col_s:
            st.markdown("**🐇 Always 8B (small)**")
            with st.spinner("Running 8B…"):
                small = run_fixed_model(final_query, SMALL_MODEL)
            st.metric("Model", "8B")
            st.metric("Complexity", "—")
            st.metric("Latency", f"{small.llm_latency_ms:.0f} ms")
            st.metric("Tokens out", small.tokens_out)
            with st.container(border=True):
                st.write(small.output[:500])

        with col_l:
            st.markdown("**🦁 Always 70B (large)**")
            with st.spinner("Running 70B…"):
                large = run_fixed_model(final_query, LARGE_MODEL)
            st.metric("Model", "70B")
            st.metric("Complexity", "—")
            st.metric("Latency", f"{large.llm_latency_ms:.0f} ms")
            st.metric("Tokens out", large.tokens_out)
            with st.container(border=True):
                st.write(large.output[:500])

        st.divider()
        st.markdown("#### Cost vs Quality Trade-off Summary")
        st.table({
            "Strategy": ["Routed", "Always 8B", "Always 70B"],
            "Model used": [routed.routing.model_selected, SMALL_MODEL, LARGE_MODEL],
            "Total latency (ms)": [f"{routed.total_latency_ms:.0f}", f"{small.llm_latency_ms:.0f}", f"{large.llm_latency_ms:.0f}"],
            "Est. relative cost": [
                "Optimal" if routed.routing.complexity == "SIMPLE" else "High",
                "Low",
                "High",
            ],
        })
