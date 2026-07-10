"""Loan Eligibility — AI Agent (T5) application entry point."""

import streamlit as st
from core.launcher import go_home
from app.components.step_nav import render_page_nav, render_stepper

from applications.loan_agent.constants import (
    APPLICATION_PAGE_LABEL,
    NAVIGATION_SESSION_KEY,
)
from applications.loan_agent.pages import (
    application,
    decision,
    download,
    history,
    run,
)

PAGES = {
    APPLICATION_PAGE_LABEL: application.render,
    "🤖 Run Agent": run.render,
    "📄 Decision": decision.render,
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
                    <div class="aiew-tb-title">Autonomous Loan Evaluator</div>
                    <div class="aiew-tb-desc">
                        Agentic workflow — three deterministic tools (validate, risk metrics,
                        policy lookup) run sequentially, then an LLM synthesises a structured
                        APPROVED / DECLINED / MANUAL_REVIEW decision with full reasoning.
                    </div>
                    <div class="aiew-tb-flow">📋 Apply → 🔧 Validate → 📊 Risk → 📜 Policy → 🤖 Synthesise → 📄 Decision</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain tools</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">llama-3.1-8b</span>
                        <span class="aiew-tech-pill">pandas</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">Loan Agent · T5 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Apply → Run → Decide → Export")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
