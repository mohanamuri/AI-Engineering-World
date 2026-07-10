import streamlit as st
from core.launcher import go_home
from app.components.step_nav import render_page_nav, render_stepper

from applications.hr_agent.constants import NAVIGATION_SESSION_KEY
from applications.hr_agent.pages import application, run, history, download


PAGES = {
    "👤 Employee Profile": application.render,
    "🚀 Run Agent": run.render,
    "📜 History": history.render,
    "⬇ Download": download.render,
}


def run_app() -> None:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t5">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">T5</div>
                <div>
                    <div class="aiew-tb-cap">AI Agent · Tier 5 of 6</div>
                    <div class="aiew-tb-title">HR Analytics — Attrition Risk Agent</div>
                    <div class="aiew-tb-desc">
                        A single autonomous agent validates employee data, computes an
                        evidence-based attrition risk score, looks up retention policy,
                        and synthesises a structured risk report with actionable interventions.
                    </div>
                    <div class="aiew-tb-flow">👤 Profile → 🤖 Validate → 📊 Score → 📋 Policy → 📝 Report</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">LangChain Tools</span>
                        <span class="aiew-tech-pill">llama-3.1-8b</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">HR Analytics · T5 workflow</div>', unsafe_allow_html=True)
        if "hr_agent_nav_pending" in st.session_state:
            st.session_state[NAVIGATION_SESSION_KEY] = st.session_state.pop("hr_agent_nav_pending")
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Profile → Agent → Report → Export")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
