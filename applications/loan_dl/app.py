"""Loan Eligibility — Deep Learning application entry point."""

import streamlit as st
from core.launcher import go_home
from app.components.step_nav import render_page_nav, render_stepper

from applications.loan_dl.constants import (
    NAVIGATION_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.loan_dl.pages import (
    download,
    evaluate,
    explore,
    preprocess,
    train,
    upload,
)


PAGES = {
    UPLOAD_PAGE_LABEL: upload.render,
    "📊 Explore Data": explore.render,
    "🧹 Preprocess": preprocess.render,
    "🧠 Train Neural Network": train.render,
    "📈 Evaluate Model": evaluate.render,
    "⬇ Download Model": download.render,
}


def run() -> None:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t2">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">T2</div>
                <div>
                    <div class="aiew-tb-cap">Deep Learning · Tier 2 of 6</div>
                    <div class="aiew-tb-title">Loan Eligibility Prediction</div>
                    <div class="aiew-tb-desc">
                        Neural network workflow — same pipeline as T1, but the model is
                        a multi-layer perceptron. Compare loss curves, convergence, and
                        accuracy against the classical baseline.
                    </div>
                    <div class="aiew-tb-flow">📤 Upload → 📊 Explore → 🧹 Preprocess → 🧠 Train MLP → 📈 Evaluate → ⬇ Export</div>
                    <div>
                        <span class="aiew-tech-pill">sklearn MLPClassifier</span>
                        <span class="aiew-tech-pill">pandas</span>
                        <span class="aiew-tech-pill">plotly</span>
                        <span class="aiew-tech-pill">joblib</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">Loan DL · T2 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Data → Features → Network → Evaluation")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
