"""UC2 — Playground: Interactive model routing demo."""

import streamlit as st

from applications.aiopt_projects.services.model_router import LARGE_MODEL, SMALL_MODEL, run_routed
from applications.aiopt_projects.uc2.constants import QUERY_SESSION_KEY, ROUTED_RESULT_KEY

EXAMPLE_QUERIES = {
    "Simple — factual": "What is the speed of light?",
    "Simple — definition": "What is machine learning?",
    "Simple — calculation": "What is 15 % of 240?",
    "Complex — analysis": "Compare transformer vs LSTM architectures for time-series forecasting. When would you choose each?",
    "Complex — code": "Write a Python function that implements a binary search tree with insert, search, and delete methods.",
    "Complex — strategy": "Design a data pipeline architecture for a real-time fraud detection system processing 10k transactions per second.",
}


def render() -> None:
    st.subheader("🧪 Playground — Model Routing")

    with st.expander("Quick-start examples"):
        for label, query in EXAMPLE_QUERIES.items():
            if st.button(label, key=f"aiopt_uc2_ex_{label}"):
                st.session_state[QUERY_SESSION_KEY] = query
                st.rerun()

    query = st.text_area(
        "Enter your query",
        value=st.session_state.get(QUERY_SESSION_KEY, ""),
        height=100,
        placeholder="Ask anything — the router will classify and select the right model.",
        key=QUERY_SESSION_KEY,
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="aiopt_uc2_temp")

    if st.button("Route & Run", type="primary", disabled=not query.strip()):
        with st.spinner("Classifying query and selecting model…"):
            result = run_routed(query.strip(), temperature=temperature)
        st.session_state[ROUTED_RESULT_KEY] = result
        st.rerun()

    result = st.session_state.get(ROUTED_RESULT_KEY)
    if result:
        badge_colour = "🟠" if result.routing.complexity == "COMPLEX" else "🟢"
        st.markdown(f"### {badge_colour} Routed to: `{result.routing.model_selected}`")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Complexity", result.routing.complexity)
        c2.metric("Routing latency", f"{result.routing.routing_latency_ms:.0f} ms")
        c3.metric("LLM latency", f"{result.llm_latency_ms:.0f} ms")
        c4.metric("Total latency", f"{result.total_latency_ms:.0f} ms")

        with st.container(border=True):
            st.markdown(f"**Routing reason:** {result.routing.routing_reason}")

        with st.container(border=True):
            st.markdown("**Response**")
            st.write(result.output)

        if result.routing.complexity == "SIMPLE":
            savings_pct = 70
            st.info(
                f"This query was routed to the **8B model** — estimated **~{savings_pct} % cost saving** "
                "vs always using the 70B model."
            )
        else:
            st.warning(
                "This query was routed to the **70B model** — full capability applied. "
                "Cost is higher but quality is maximised."
            )
