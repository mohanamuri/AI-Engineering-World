"""Loan Eligibility — Multi-Agent System (T6) application entry point."""

import streamlit as st
from core.launcher import go_home

from applications.loan_multi_agent.constants import (
    APPLICATION_PAGE_LABEL,
    NAVIGATION_SESSION_KEY,
)
from applications.loan_multi_agent.pages import (
    application,
    consensus,
    download,
    history,
    panel,
)

PAGES = {
    APPLICATION_PAGE_LABEL: application.render,
    "🏛️ Run Panel":  panel.render,
    "📄 Consensus":   consensus.render,
    "📜 History":     history.render,
    "⬇ Download":     download.render,
}


def run() -> None:
    if st.button("← Platform home"):
        go_home()
        st.rerun()

    st.markdown(
        """
        <section class="aiew-loan-hero">
            <div class="aiew-app-icon" style="font-size:.55rem;">MAS</div>
            <div>
                <h1>Loan Eligibility Prediction</h1>
                <p>
                    Multi-Agent System · Underwriter, Fraud Detector, and Compliance Officer
                    each review independently. A Supervisor synthesises the consensus decision.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Loan Multi-Agent workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Apply → Panel → Consensus → Export")

    PAGES[page]()
