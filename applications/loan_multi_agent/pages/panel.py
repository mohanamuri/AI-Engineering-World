"""Run the multi-agent panel and show all specialist reports — page 2."""

from __future__ import annotations

import streamlit as st

from applications.loan_multi_agent.constants import (
    AGENT_CONFIG_SESSION_KEY,
    APPLICATION_SESSION_KEY,
    HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PANEL_RESULT_SESSION_KEY,
)
from applications.loan_multi_agent.services.panel_graph import (
    AgentConfig,
    PanelRunResult,
    run_panel,
)
from applications.loan_multi_agent.services.specialist_agents import SpecialistReport

_REC_META = {
    "RECOMMEND_APPROVE":  {"color": "#059669", "label": "Approve",  "icon": "✅"},
    "RECOMMEND_DECLINE":  {"color": "#dc2626", "label": "Decline",  "icon": "❌"},
    "RECOMMEND_REVIEW":   {"color": "#d97706", "label": "Review",   "icon": "⚠️"},
}


def render() -> None:
    st.header("🏛️ Run Panel")
    st.caption(
        "Three specialist agents review the application independently. "
        "A Supervisor then synthesises their reports into a consensus decision."
    )

    application: dict | None = st.session_state.get(APPLICATION_SESSION_KEY)
    if application is None:
        with st.container(border=True):
            st.warning("No application loaded.")
            st.button("← Go to Application", type="primary",
                on_click=lambda: st.session_state.update(
                    {NAVIGATION_SESSION_KEY: "📋 Application"}))
        return

    config: AgentConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, AgentConfig())
    with st.expander("⚙️ Agent settings", expanded=False):
        llm = st.text_input("LLM model (Groq)", value=config.llm_model)
        temp = st.slider("Temperature", 0.0, 1.0, value=config.temperature, step=0.05)
        config = AgentConfig(llm_model=llm, temperature=temp)
        st.session_state[AGENT_CONFIG_SESSION_KEY] = config

    # ---- Application summary --------------------------------------------
    with st.container(border=True):
        st.markdown(f"**Applicant:** {application.get('applicant_name', 'Unknown')}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Loan amount", f"${application.get('loan_amount_usd', 0):,.0f}")
        m2.metric("Credit score", application.get("credit_score", "—"))
        m3.metric("Monthly income", f"${application.get('monthly_income_usd', 0):,.0f}")
        m4.metric("Tenure", f"{application.get('loan_tenure_months', 0)} mo")

    if st.button("▶ Convene Credit Committee", type="primary", use_container_width=True):
        _run_and_store(application, config)
        st.rerun()

    # ---- Panel results --------------------------------------------------
    result: PanelRunResult | None = st.session_state.get(PANEL_RESULT_SESSION_KEY)
    if result is not None:
        st.divider()
        _render_panel(result)


def _run_and_store(application: dict, config: AgentConfig) -> None:
    with st.spinner(
        f"Convening panel with **{config.llm_model}** … "
        "3 specialists + 1 supervisor — may take 60–90 seconds."
    ):
        try:
            result = run_panel(application, config)
        except Exception as exc:
            st.error(f"Panel run failed: {exc}\n\nCheck that your GROQ_API_KEY is set and the model name is correct.")
            return

    st.session_state[PANEL_RESULT_SESSION_KEY] = result
    st.session_state.setdefault(HISTORY_SESSION_KEY, []).append(result)


def _render_panel(result: PanelRunResult) -> None:
    st.subheader("Specialist reports")

    reports = [result.underwriter_report, result.fraud_report, result.compliance_report]
    cols = st.columns(3)

    for col, report in zip(cols, reports):
        meta = _REC_META.get(report.recommendation, _REC_META["RECOMMEND_REVIEW"])
        with col:
            st.markdown(
                f"<div style='text-align:center;padding:.5rem 0 .25rem;'>"
                f"<div style='font-size:1.5rem;'>{report.icon}</div>"
                f"<div style='font-size:.8rem;font-weight:700;color:#0f172a;margin:.2rem 0 .1rem;'>"
                f"{report.agent_name}</div>"
                f"<div style='font-size:.65rem;color:#64748b;margin-bottom:.4rem;'>{report.agent_role}</div>"
                f"<div style='font-size:.7rem;font-weight:700;color:{meta['color']};'>"
                f"{meta['icon']} {meta['label']}</div></div>",
                unsafe_allow_html=True,
            )
            with st.expander("View report", expanded=False):
                st.markdown(report.analysis)
                st.caption(f"{len(report.tool_steps)} tool calls")

    # ---- Supervisor decision -------------------------------------------
    st.divider()
    _DECISION_META = {
        "APPROVED":      {"color": "#059669", "bg": "#dcfce7", "border": "#86efac", "icon": "✅"},
        "DECLINED":      {"color": "#dc2626", "bg": "#fee2e2", "border": "#fca5a5", "icon": "❌"},
        "MANUAL_REVIEW": {"color": "#d97706", "bg": "#fef9c3", "border": "#fde047", "icon": "⚠️"},
        "UNKNOWN":       {"color": "#6366f1", "bg": "#eef2ff", "border": "#c7d2fe", "icon": "❓"},
    }
    meta = _DECISION_META.get(result.decision, _DECISION_META["UNKNOWN"])

    st.markdown(
        f"""
        <div style="background:{meta['bg']};border:1px solid {meta['border']};
                    border-radius:.85rem;padding:1.25rem 1.5rem;">
            <div style="font-size:1.1rem;color:#64748b;margin-bottom:.25rem;">
                ⚖️ Supervisor — Credit Committee
            </div>
            <div style="font-size:1.5rem;font-weight:800;color:{meta['color']};">
                {meta['icon']} {result.decision.replace('_', ' ')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Supervisor reasoning", expanded=True):
        st.markdown(result.final_answer)

    st.divider()
    st.button(
        "→ View Full Consensus Report",
        type="primary",
        on_click=lambda: st.session_state.update(
            {NAVIGATION_SESSION_KEY: "📄 Consensus"}
        ),
    )
