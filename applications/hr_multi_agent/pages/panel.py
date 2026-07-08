"""Panel execution page — runs all three specialists + HR Director."""

from __future__ import annotations
import streamlit as st

from applications.hr_multi_agent.constants import AGENT_CONFIG_SESSION_KEY, PANEL_RUN_HISTORY_SESSION_KEY
from applications.hr_multi_agent.services.panel_graph import AgentConfig, PanelRunResult, run_panel
from applications.shared.api_reference import render_api_reference

_RISK_COLOR = {"HIGH": "#ef4444", "MEDIUM": "#f97316", "LOW": "#22c55e", "UNKNOWN": "#94a3b8"}
_REC_COLOR = {"HIGH_RISK": "#ef4444", "INTERVENE": "#f97316", "RETAIN": "#22c55e"}
_REC_LABEL = {"HIGH_RISK": "🔴 HIGH RISK", "INTERVENE": "🟡 INTERVENE", "RETAIN": "🟢 RETAIN"}


def render() -> None:
    st.header("👥 Expert Panel")

    employee = st.session_state.get("hr_ma_pending_employee")
    config = st.session_state.get("hr_ma_pending_config",
                                   st.session_state.get(AGENT_CONFIG_SESSION_KEY, AgentConfig()))

    if employee is None:
        st.warning("Enter an employee profile first.")
        st.button("← Go to Employee Profile",
                  on_click=lambda: st.session_state.update({"hr_multi_agent_navigation": "👤 Employee Profile"}))
        return

    history = st.session_state.setdefault(PANEL_RUN_HISTORY_SESSION_KEY, [])

    if st.button("▶ Convene Panel", use_container_width=True, type="primary"):
        _do_run(employee, config, history)

    if st.session_state.pop("hr_ma_auto_run", False):
        _do_run(employee, config, history)
        st.rerun()

    if not history:
        return

    latest: PanelRunResult = history[-1]
    _render_panel(latest)
    render_api_reference("hr_multi_agent", "panel")


def _do_run(employee, config, history):
    with st.spinner("Three specialists analysing in parallel…"):
        try:
            result = run_panel(employee, config)
        except Exception as exc:
            st.error(f"Panel failed: {exc}\nCheck GROQ_API_KEY.")
            return
    history.append(result)
    st.success("Panel complete.")


def _render_panel(r: PanelRunResult) -> None:
    # Consensus header
    color = _RISK_COLOR.get(r.risk_level, "#94a3b8")
    st.markdown(
        f"<div style='background:{color}20;border-left:4px solid {color};"
        f"padding:1rem;border-radius:0.5rem;margin:1rem 0;'>"
        f"<strong style='font-size:1.3rem;color:{color};'>HR Director Decision: {r.risk_level} RISK</strong>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Specialist badges
    cols = st.columns(3)
    for col, report, name in zip(
        cols,
        [r.hr_manager_report, r.perf_evaluator_report, r.risk_assessor_report],
        ["HR Manager", "Performance Evaluator", "Risk Assessor"],
    ):
        rec = report.recommendation
        rc = _REC_COLOR.get(rec, "#94a3b8")
        with col:
            st.markdown(
                f"<div style='text-align:center;background:{rc}20;"
                f"border:1px solid {rc};padding:.75rem;border-radius:.5rem;'>"
                f"<div style='font-weight:600;'>{name}</div>"
                f"<div style='color:{rc};font-size:.9rem;margin-top:.25rem;'>"
                f"{_REC_LABEL.get(rec, rec)}</div></div>",
                unsafe_allow_html=True,
            )

    st.divider()

    tab_director, tab_hr, tab_perf, tab_risk = st.tabs([
        "📋 Director Decision", "👔 HR Manager", "📈 Performance", "⚠️ Risk Assessor"
    ])

    with tab_director:
        st.markdown(r.final_answer)

    for tab, report in [(tab_hr, r.hr_manager_report), (tab_perf, r.perf_evaluator_report), (tab_risk, r.risk_assessor_report)]:
        with tab:
            st.markdown(report.analysis)
