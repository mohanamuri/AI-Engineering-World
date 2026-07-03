"""Loan Eligibility — AI Agent (T5) application entry point."""

import streamlit as st
from core.launcher import go_home

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
    if st.button("← Platform home"):
        go_home()
        st.rerun()

    st.markdown(
        """
        <section class="aiew-loan-hero">
            <div class="aiew-app-icon" style="font-size:.55rem;">AGT</div>
            <div>
                <h1>Loan Eligibility Prediction</h1>
                <p>
                    AI Agent · A single LangGraph ReAct agent autonomously validates
                    the application, scores risk, and produces a structured decision report.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Loan Agent workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            key=NAVIGATION_SESSION_KEY,
        )
        st.caption("Apply → Run → Decide → Export")

    PAGES[page]()
