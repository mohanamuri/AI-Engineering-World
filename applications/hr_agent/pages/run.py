"""Agent run page — executes and displays the HR attrition risk assessment."""

from __future__ import annotations
import streamlit as st

from applications.hr_agent.constants import AGENT_RUN_HISTORY_SESSION_KEY, AGENT_CONFIG_SESSION_KEY
from applications.hr_agent.services.agent_graph import AgentConfig, AgentRunResult, run_agent
from applications.shared.api_reference import render_api_reference


_RISK_COLORS = {"HIGH": "#ef4444", "MEDIUM": "#f97316", "LOW": "#22c55e", "UNKNOWN": "#94a3b8"}
_RISK_ICONS = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "UNKNOWN": "⚪"}


def render() -> None:
    st.header("🚀 Run Agent")

    employee = st.session_state.get("hr_agent_pending_employee")
    config: AgentConfig = st.session_state.get("hr_agent_pending_config",
                                                st.session_state.get(AGENT_CONFIG_SESSION_KEY, AgentConfig()))

    if employee is None:
        st.warning("Enter an employee profile on the **Employee Profile** page first.")
        st.button("← Go to Employee Profile",
                  on_click=lambda: st.session_state.update({"hr_agent_navigation": "👤 Employee Profile"}))
        return

    # Auto-run if triggered from profile page
    history = st.session_state.setdefault(AGENT_RUN_HISTORY_SESSION_KEY, [])

    if st.button("▶ Run Assessment", use_container_width=True, type="primary"):
        _do_run(employee, config, history)

    # Auto-run on first navigate
    if st.session_state.pop(AGENT_RUN_HISTORY_SESSION_KEY + "_navigate", False):
        _do_run(employee, config, history)
        st.rerun()

    if not history:
        return

    latest: AgentRunResult = history[-1]
    _render_result(latest)
    render_api_reference("hr_agent", "run")


def _do_run(employee, config, history):
    with st.spinner("Agent running… (validate → score → policy lookup → synthesise)"):
        try:
            result = run_agent(employee, config)
        except Exception as exc:
            st.error(f"Agent failed: {exc}\nCheck GROQ_API_KEY.")
            return
    history.append(result)
    st.success("Assessment complete.")


def _render_result(result: AgentRunResult) -> None:
    risk = result.risk_level
    color = _RISK_COLORS.get(risk, "#94a3b8")
    icon = _RISK_ICONS.get(risk, "⚪")

    # Risk banner
    st.markdown(
        f"<div style='background:{color}20;border-left:4px solid {color};"
        f"padding:1rem;border-radius:0.5rem;margin-bottom:1rem;'>"
        f"<span style='font-size:1.5rem;'>{icon}</span> "
        f"<strong style='font-size:1.2rem;color:{color};'>{risk} RISK</strong>"
        f" — Score: {result.risk_score}/100"
        f"</div>",
        unsafe_allow_html=True,
    )

    tab_report, tab_steps = st.tabs(["📋 Risk Report", "🔧 Agent Steps"])

    with tab_report:
        st.markdown(result.final_answer)

    with tab_steps:
        st.caption(f"3 tools executed · {len(result.steps)} steps · Model: llama-3.3-70b-versatile")
        for i, step in enumerate(result.steps, 1):
            with st.expander(f"Step {i} — `{step.tool_name}`"):
                st.markdown("**Input:**")
                st.code(step.tool_input[:500] + ("…" if len(step.tool_input) > 500 else ""), language="json")
                st.markdown("**Output:**")
                st.text(step.tool_output)
