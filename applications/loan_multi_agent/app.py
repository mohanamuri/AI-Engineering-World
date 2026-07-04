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
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t6">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">T6</div>
                <div>
                    <div class="aiew-tb-cap">Multi-Agent System · Tier 6 of 6</div>
                    <div class="aiew-tb-title">Credit Committee Panel</div>
                    <div class="aiew-tb-desc">
                        Three specialist agents run in parallel — Underwriter 💼, Fraud Detector 🔎,
                        Compliance Officer ⚖️. A Supervisor resolves disagreements and issues the
                        final binding decision. Built with LangGraph StateGraph fan-out.
                    </div>
                    <div class="aiew-tb-flow">📋 Apply → 🏛️ Panel (×3 parallel) → 📄 Consensus → 📜 History → ⬇ Export</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">StateGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">llama-3.1-8b</span>
                        <span class="aiew-tech-pill">parallel fan-out</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">Loan MAS · T6 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Apply → Panel → Consensus → Export")

    PAGES[page]()
