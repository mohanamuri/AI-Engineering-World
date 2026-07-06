"""Employee profile input for the HR Multi-Agent panel."""

import streamlit as st
from applications.hr_multi_agent.constants import AGENT_CONFIG_SESSION_KEY, PANEL_RUN_HISTORY_SESSION_KEY
from applications.hr_multi_agent.services.panel_graph import AgentConfig


_DEFAULT = {
    "Age": 32, "Department": "Sales", "JobRole": "Sales Representative",
    "JobSatisfaction": 2, "EnvironmentSatisfaction": 2, "WorkLifeBalance": 1,
    "OverTime": "Yes", "YearsAtCompany": 4, "YearsSinceLastPromotion": 4,
    "MonthlyIncome": 3500, "NumCompaniesWorked": 4, "TotalWorkingYears": 8,
    "JobLevel": 1, "MaritalStatus": "Single", "StockOptionLevel": 0,
    "PerformanceRating": 3, "TrainingTimesLastYear": 1,
}


def render() -> None:
    st.header("👤 Employee Profile")
    st.caption(
        "Three specialist agents — HR Manager, Performance Evaluator, and Risk Assessor — "
        "each independently analyse the employee. The HR Director synthesises a consensus decision."
    )

    config = st.session_state.get(AGENT_CONFIG_SESSION_KEY, AgentConfig())
    with st.expander("⚙️ Configuration"):
        llm = st.text_input("LLM model (Groq)", config.llm_model)
        temp = st.slider("Temperature", 0.0, 1.0, config.temperature, 0.05)
        config = AgentConfig(llm_model=llm, temperature=temp)
        st.session_state[AGENT_CONFIG_SESSION_KEY] = config

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", 18, 70, _DEFAULT["Age"])
        dept = st.text_input("Department", _DEFAULT["Department"])
        job_role = st.text_input("Job Role", _DEFAULT["JobRole"])
        job_level = st.number_input("Job Level (1-5)", 1, 5, _DEFAULT["JobLevel"])
    with col2:
        job_sat = st.selectbox("Job Satisfaction (1=Low)", [1, 2, 3, 4], index=_DEFAULT["JobSatisfaction"]-1)
        env_sat = st.selectbox("Environment Satisfaction (1=Low)", [1, 2, 3, 4], index=_DEFAULT["EnvironmentSatisfaction"]-1)
        wlb = st.selectbox("Work-Life Balance (1=Bad)", [1, 2, 3, 4], index=_DEFAULT["WorkLifeBalance"]-1)
        overtime = st.selectbox("OverTime", ["Yes", "No"])
    with col3:
        years_co = st.number_input("Years at Company", 0, 40, _DEFAULT["YearsAtCompany"])
        yslp = st.number_input("Years Since Last Promotion", 0, 20, _DEFAULT["YearsSinceLastPromotion"])
        income = st.number_input("Monthly Income ($)", 1000, 50000, _DEFAULT["MonthlyIncome"], 500)
        num_co = st.number_input("Num Companies Worked", 0, 15, _DEFAULT["NumCompaniesWorked"])
        total_yrs = st.number_input("Total Working Years", 0, 40, _DEFAULT["TotalWorkingYears"])

    employee = {
        "Age": age, "Department": dept, "JobRole": job_role, "JobLevel": job_level,
        "JobSatisfaction": job_sat, "EnvironmentSatisfaction": env_sat,
        "WorkLifeBalance": wlb, "OverTime": overtime,
        "YearsAtCompany": years_co, "YearsSinceLastPromotion": yslp,
        "MonthlyIncome": income, "NumCompaniesWorked": num_co,
        "TotalWorkingYears": total_yrs, "MaritalStatus": "Single",
        "StockOptionLevel": 0, "PerformanceRating": 3, "TrainingTimesLastYear": 1,
    }

    if st.button("🤖 Convene Expert Panel", use_container_width=True, type="primary"):
        st.session_state["hr_ma_pending_employee"] = employee
        st.session_state["hr_ma_pending_config"] = config
        st.session_state["hr_ma_auto_run"] = True
        st.session_state["hr_ma_nav_pending"] = "👥 Panel"
        st.rerun()
