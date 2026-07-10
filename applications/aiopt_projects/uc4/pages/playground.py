"""UC4 — Playground: Streaming and Fallback demos."""

import streamlit as st

from applications.aiopt_projects.services.streaming_fallback import (
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    run_with_fallback,
    stream_response,
)
from applications.aiopt_projects.uc4.constants import (
    FALLBACK_RESULT_KEY,
    STREAM_PROMPT_KEY,
)

EXAMPLE_PROMPTS = [
    "Explain how neural networks learn from data.",
    "Write a short poem about the ocean at night.",
    "What are the main differences between SQL and NoSQL databases?",
    "Describe how GPS works in simple terms.",
]


def render() -> None:
    st.subheader("🧪 Playground — Streaming + Fallback")

    tab_stream, tab_fallback = st.tabs(["⚡ Streaming", "🛡️ Fallback"])

    # ─── Streaming tab ───────────────────────────────────────────────────────
    with tab_stream:
        st.markdown(
            "Watch tokens appear in real time. "
            "Compare the *feel* of streaming vs waiting for the full response."
        )

        prompt = st.text_area(
            "Prompt",
            value=st.session_state.get(STREAM_PROMPT_KEY, EXAMPLE_PROMPTS[0]),
            height=80,
            key=STREAM_PROMPT_KEY,
        )
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="aiopt_uc4_stream_temp")

        col_s, col_b = st.columns(2)
        with col_s:
            st.markdown("**⚡ Streaming response**")
            if st.button("Run (streaming)", type="primary", key="aiopt_uc4_btn_stream"):
                if prompt.strip():
                    st.write_stream(
                        stream_response(prompt.strip(), temperature=temperature)
                    )
                    st.caption(f"Model: {PRIMARY_MODEL}")

        with col_b:
            st.markdown("**🐢 Blocking response (for comparison)**")
            if st.button("Run (blocking)", key="aiopt_uc4_btn_block"):
                if prompt.strip():
                    with st.spinner("Waiting for full response…"):
                        from applications.aiopt_projects.services.streaming_fallback import run_blocking
                        result = run_blocking(prompt.strip(), temperature=temperature)
                    st.write(result.output)
                    st.caption(
                        f"Model: {result.model_used} · "
                        f"{result.latency_ms:.0f} ms · "
                        f"{result.tokens_out} tokens out"
                    )

        st.info(
            "Notice: the streaming version *feels* faster even though total generation time is the same. "
            "That's the UX power of streaming — perceived latency is the metric that matters."
        )

    # ─── Fallback tab ────────────────────────────────────────────────────────
    with tab_fallback:
        st.markdown(
            "Simulate a primary model failure and watch the fallback kick in automatically."
        )

        fallback_prompt = st.text_area(
            "Prompt",
            value=EXAMPLE_PROMPTS[2],
            height=80,
            key="aiopt_uc4_fallback_prompt",
        )

        force_fail = st.checkbox(
            "🔴 Simulate primary model failure (force fallback)",
            value=False,
            help="When checked, the service skips the primary model entirely to demonstrate fallback.",
        )

        if st.button("Run with fallback logic", type="primary", key="aiopt_uc4_btn_fallback"):
            if fallback_prompt.strip():
                with st.spinner("Running with fallback logic…"):
                    result = run_with_fallback(
                        fallback_prompt.strip(),
                        force_fallback=force_fail,
                    )
                st.session_state[FALLBACK_RESULT_KEY] = result
                st.rerun()

        result = st.session_state.get(FALLBACK_RESULT_KEY)
        if result:
            if result.fell_back:
                st.warning(
                    f"**Fell back to `{result.model_used}`** after {result.attempts} attempt(s). "
                    + (f"Primary error: `{result.error_message[:100]}`" if result.error_message else "")
                )
            else:
                st.success(f"**Primary model succeeded** on attempt {result.attempts} using `{result.model_used}`.")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Model used", result.model_used.split("-")[0] + "…")
            c2.metric("Fell back?", "Yes" if result.fell_back else "No")
            c3.metric("Attempts", result.attempts)
            c4.metric("Latency", f"{result.latency_ms:.0f} ms")

            with st.container(border=True):
                st.markdown("**Response**")
                st.write(result.output)
