"""Employee profile input page for the HR Agent workflow."""

import streamlit as st

from applications.hr_agent.constants import AGENT_CONFIG_SESSION_KEY, AGENT_RUN_HISTORY_SESSION_KEY
from applications.hr_agent.services.agent_graph import AgentConfig


_DEFAULT_EMPLOYEE = {
    "Age": 32,
    "Department": "Sales",
    "JobRole": "Sales Representative",
    "JobSatisfaction": 2,
    "EnvironmentSatisfaction": 2,
    "WorkLifeBalance": 1,
    "OverTime": "Yes",
    "YearsAtCompany": 4,
    "YearsSinceLastPromotion": 4,
    "MonthlyIncome": 3500,
    "NumCompaniesWorked": 4,
    "TotalWorkingYears": 8,
    "JobLevel": 1,
    "MaritalStatus": "Single",
    "StockOptionLevel": 0,
}


def render() -> None:
    st.header("👤 Employee Profile")
    st.caption(
        "Enter an employee's details. The agent will validate the data, "
        "compute an attrition risk score, look up retention policy, "
        "and synthesise a structured risk report."
    )

    config: AgentConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, AgentConfig())

    with st.expander("⚙️ Agent configuration"):
        llm_model = st.text_input("LLM model (Groq)", config.llm_model)
        temperature = st.slider("Temperature", 0.0, 1.0, config.temperature, 0.05)
        config = AgentConfig(llm_model=llm_model, temperature=temperature)
        st.session_state[AGENT_CONFIG_SESSION_KEY] = config

    st.subheader("Employee details")
    st.info("Pre-filled with a high-risk example profile. Edit any field and click **Run Agent**.")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", 18, 70, _DEFAULT_EMPLOYEE["Age"])
        dept = st.text_input("Department", _DEFAULT_EMPLOYEE["Department"])
        job_role = st.text_input("Job Role", _DEFAULT_EMPLOYEE["JobRole"])
        marital = st.selectbox("Marital Status", ["Single", "Married", "Divorced"])
    with col2:
        job_sat = st.selectbox("Job Satisfaction (1=Low, 4=High)", [1, 2, 3, 4],
                               index=_DEFAULT_EMPLOYEE["JobSatisfaction"] - 1)
        env_sat = st.selectbox("Environment Satisfaction (1=Low, 4=High)", [1, 2, 3, 4],
                               index=_DEFAULT_EMPLOYEE["EnvironmentSatisfaction"] - 1)
        wlb = st.selectbox("Work-Life Balance (1=Bad, 4=Best)", [1, 2, 3, 4],
                            index=_DEFAULT_EMPLOYEE["WorkLifeBalance"] - 1)
        overtime = st.selectbox("OverTime", ["Yes", "No"])
    with col3:
        years_company = st.number_input("Years at Company", 0, 40, _DEFAULT_EMPLOYEE["YearsAtCompany"])
        yslp = st.number_input("Years Since Last Promotion", 0, 20, _DEFAULT_EMPLOYEE["YearsSinceLastPromotion"])
        monthly_income = st.number_input("Monthly Income ($)", 1000, 50000, _DEFAULT_EMPLOYEE["MonthlyIncome"], 500)
        num_companies = st.number_input("Num Companies Worked", 0, 15, _DEFAULT_EMPLOYEE["NumCompaniesWorked"])
        total_yrs = st.number_input("Total Working Years", 0, 40, _DEFAULT_EMPLOYEE["TotalWorkingYears"])

    employee = {
        "Age": age, "Department": dept, "JobRole": job_role, "MaritalStatus": marital,
        "JobSatisfaction": job_sat, "EnvironmentSatisfaction": env_sat,
        "WorkLifeBalance": wlb, "OverTime": overtime,
        "YearsAtCompany": years_company, "YearsSinceLastPromotion": yslp,
        "MonthlyIncome": monthly_income, "NumCompaniesWorked": num_companies,
        "TotalWorkingYears": total_yrs, "JobLevel": 1, "StockOptionLevel": 0,
    }

    if st.button("🤖 Run Agent — Assess Attrition Risk", use_container_width=True, type="primary"):
        st.session_state["hr_agent_pending_employee"] = employee
        st.session_state["hr_agent_pending_config"] = config
        st.session_state[AGENT_RUN_HISTORY_SESSION_KEY + "_navigate"] = True
        st.session_state["hr_agent_nav_pending"] = "🚀 Run Agent"
        st.rerun()
