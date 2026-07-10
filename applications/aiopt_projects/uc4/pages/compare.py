"""UC4 — Compare: Streaming vs blocking latency, primary vs fallback resilience."""

import time

import streamlit as st

from applications.aiopt_projects.services.streaming_fallback import (
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    run_blocking,
    run_with_fallback,
)


def render() -> None:
    st.subheader("⚖️ Compare — Streaming vs Blocking · Primary vs Fallback")

    st.markdown(
        "Two side-by-side comparisons: "
        "(1) Streaming vs blocking on the same prompt. "
        "(2) Primary model success vs forced fallback."
    )

    # Section 1: Streaming vs Blocking
    st.markdown("### ⚡ Section 1: Streaming vs Blocking")
    st.caption("Run the same prompt and compare time-to-first-token vs time-to-full-response.")

    prompt = st.text_area(
        "Prompt",
        value="Explain the concept of entropy in thermodynamics and information theory.",
        key="aiopt_uc4_cmp_prompt",
        height=80,
    )

    if st.button("Compare streaming vs blocking", type="primary", key="aiopt_uc4_cmp_btn1"):
        col_s, col_b = st.columns(2)

        with col_s:
            st.markdown("**⚡ Streaming**")
            t_start = time.perf_counter()
            token_container = st.empty()
            collected = []
            first_token_ms = None
            for token in __import__(
                "applications.aiopt_projects.services.streaming_fallback",
                fromlist=["stream_response"]
            ).stream_response(prompt.strip()):
                if first_token_ms is None:
                    first_token_ms = (time.perf_counter() - t_start) * 1000
                collected.append(token)
                token_container.write("".join(collected))
            total_stream_ms = (time.perf_counter() - t_start) * 1000
            st.metric("Time to first token", f"{first_token_ms:.0f} ms" if first_token_ms else "—")
            st.metric("Total time", f"{total_stream_ms:.0f} ms")
            st.caption(f"Model: {PRIMARY_MODEL}")

        with col_b:
            st.markdown("**🐢 Blocking**")
            with st.spinner("Waiting…"):
                result = run_blocking(prompt.strip())
            st.write(result.output)
            st.metric("Time to first token", f"{result.latency_ms:.0f} ms (= total)")
            st.metric("Total time", f"{result.latency_ms:.0f} ms")
            st.caption(f"Model: {result.model_used}")

    st.divider()

    # Section 2: Primary vs Fallback
    st.markdown("### 🛡️ Section 2: Primary vs Fallback")
    st.caption("Run once with the primary model succeeding, once forcing fallback — compare latency and model.")

    prompt2 = st.text_area(
        "Prompt",
        value="What are microservices and when should you use them?",
        key="aiopt_uc4_cmp_prompt2",
        height=80,
    )

    if st.button("Compare primary vs fallback", type="primary", key="aiopt_uc4_cmp_btn2"):
        col_p, col_f = st.columns(2)

        with col_p:
            st.markdown("**✅ Primary succeeds**")
            with st.spinner("Running primary…"):
                res_primary = run_with_fallback(prompt2.strip(), force_fallback=False)
            st.metric("Model", res_primary.model_used)
            st.metric("Attempts", res_primary.attempts)
            st.metric("Latency", f"{res_primary.latency_ms:.0f} ms")
            st.metric("Fell back?", "No")
            with st.container(border=True):
                st.write(res_primary.output[:400])

        with col_f:
            st.markdown("**🔄 Forced fallback**")
            with st.spinner("Simulating failure → fallback…"):
                res_fallback = run_with_fallback(prompt2.strip(), force_fallback=True)
            st.metric("Model", res_fallback.model_used)
            st.metric("Attempts", res_fallback.attempts)
            st.metric("Latency", f"{res_fallback.latency_ms:.0f} ms")
            st.metric("Fell back?", "Yes")
            with st.container(border=True):
                st.write(res_fallback.output[:400])

        st.info(
            "Notice: the fallback model is larger (70B) so quality is maintained even during primary failure. "
            "The trade-off is higher cost and potentially higher latency."
        )
