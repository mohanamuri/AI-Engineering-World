"""Loan Eligibility — Explainability (T3) application entry point."""

import streamlit as st
from core.launcher import go_home
from app.components.step_nav import render_page_nav, render_stepper

from applications.loan_xai.constants import (
    NAVIGATION_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.loan_xai.pages import (
    download,
    explain,
    explore,
    preprocess,
    train,
    upload,
)


PAGES = {
    UPLOAD_PAGE_LABEL: upload.render,
    "📊 Explore Data": explore.render,
    "🧹 Preprocess": preprocess.render,
    "🤖 Train Model": train.render,
    "🔍 Explain": explain.render,
    "⬇ Download": download.render,
}


def run() -> None:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t3">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">T3</div>
                <div>
                    <div class="aiew-tb-cap">Explainability (XAI) · Tier 3 of 6</div>
                    <div class="aiew-tb-title">Loan Eligibility Prediction</div>
                    <div class="aiew-tb-desc">
                        Model transparency workflow — train a model, then explain every prediction
                        globally and locally using SHAP and LIME. Audit-ready attribution reports.
                    </div>
                    <div class="aiew-tb-flow">📤 Upload → 📊 Explore → 🧹 Preprocess → 🤖 Train → 🔍 Explain → ⬇ Export</div>
                    <div>
                        <span class="aiew-tech-pill">SHAP</span>
                        <span class="aiew-tech-pill">LIME</span>
                        <span class="aiew-tech-pill">scikit-learn</span>
                        <span class="aiew-tech-pill">plotly</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">Loan XAI · T3 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Data → Model → Explain → Export")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
