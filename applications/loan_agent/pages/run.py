"""Run agent and show step-by-step trace — page 2 of the loan agent workflow."""

from __future__ import annotations

import streamlit as st

from applications.loan_agent.constants import (
    AGENT_CONFIG_SESSION_KEY,
    APPLICATION_SESSION_KEY,
    HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    RUN_RESULT_SESSION_KEY,
)
from applications.loan_agent.services.agent_graph import AgentConfig, AgentRunResult, run_agent


def render() -> None:
    st.header("🤖 Run Agent")
    st.caption(
        "The agent calls tools one by one — validate, score risk, look up policy — "
        "then reasons to a final decision. Every step is shown below."
    )

    application: dict | None = st.session_state.get(APPLICATION_SESSION_KEY)
    if application is None:
        with st.container(border=True):
            st.warning("No application loaded.")
            st.button(
                "← Go to Application",
                type="primary",
                on_click=lambda: st.session_state.update(
                    {NAVIGATION_SESSION_KEY: "📋 Application"}
                ),
            )
        return

    # ---- Config sidebar -------------------------------------------------
    config: AgentConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, AgentConfig())

    with st.expander("⚙️ Agent settings", expanded=False):
        llm_model = st.text_input("LLM model (Ollama)", value=config.llm_model)
        temperature = st.slider("Temperature", 0.0, 1.0, value=config.temperature, step=0.05)
        new_config = AgentConfig(llm_model=llm_model, temperature=temperature)
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config

    # ---- Application summary -------------------------------------------
    with st.container(border=True):
        st.markdown(f"**Applicant:** {application.get('applicant_name', 'Unknown')}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Loan amount", f"${application.get('loan_amount_usd', 0):,.0f}")
        m2.metric("Credit score", application.get("credit_score", "—"))
        m3.metric("Monthly income", f"${application.get('monthly_income_usd', 0):,.0f}")
        m4.metric("Tenure", f"{application.get('loan_tenure_months', 0)} mo")

    # ---- Run button -----------------------------------------------------
    if st.button("▶ Evaluate with Agent", type="primary", use_container_width=True):
        _run_and_store(application, new_config)
        st.rerun()

    # ---- Step trace -----------------------------------------------------
    result: AgentRunResult | None = st.session_state.get(RUN_RESULT_SESSION_KEY)
    if result is not None:
        st.divider()
        _render_trace(result)
        st.divider()
        st.button(
            "→ View Decision Report",
            type="primary",
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "📄 Decision"}
            ),
        )


def _run_and_store(application: dict, config: AgentConfig) -> None:
    with st.spinner(
        f"Agent thinking with **{config.llm_model}** … "
        "this may take 30–60 seconds."
    ):
        try:
            result = run_agent(application, config)
        except Exception as exc:
            st.error(
                f"Agent run failed: {exc}\n\n"
                f"Make sure Ollama is running and `{config.llm_model}` is pulled."
            )
            return

    st.session_state[RUN_RESULT_SESSION_KEY] = result

    history: list = st.session_state.setdefault(HISTORY_SESSION_KEY, [])
    history.append(result)


def _render_trace(result: AgentRunResult) -> None:
    st.subheader("Agent reasoning trace")

    _TOOL_ICONS = {
        "validate_application": "✅",
        "compute_risk_metrics": "📊",
        "lookup_policy_rule": "📖",
    }

    for i, step in enumerate(result.steps, 1):
        icon = _TOOL_ICONS.get(step.tool_name, "🔧")
        with st.expander(
            f"Step {i} · {icon} `{step.tool_name}`",
            expanded=True,
        ):
            col_in, col_out = st.columns(2)
            with col_in:
                st.markdown("**Input**")
                st.code(step.tool_input, language="json")
            with col_out:
                st.markdown("**Output**")
                st.code(step.tool_output, language="text")

    if result.final_answer:
        with st.container(border=True):
            decision_color = {
                "APPROVED": "#059669",
                "DECLINED": "#dc2626",
                "MANUAL_REVIEW": "#d97706",
            }.get(result.decision, "#6366f1")

            st.markdown(
                f"<div style='font-size:.75rem;font-weight:700;color:{decision_color};"
                f"letter-spacing:.06em;text-transform:uppercase;margin-bottom:.4rem;'>"
                f"Final answer — {result.decision}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(result.final_answer)
