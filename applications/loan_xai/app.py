"""Loan Eligibility — Explainability (T3) application entry point."""

import streamlit as st
from core.launcher import go_home

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
    if st.button("← Platform home"):
        go_home()
        st.rerun()

    st.markdown(
        """
        <section class="aiew-loan-hero">
            <div class="aiew-app-icon" style="font-size:.55rem;">XAI</div>
            <div>
                <h1>Loan Eligibility Prediction</h1>
                <p>
                    Explainability workflow · SHAP global + local attribution,
                    LIME local approximation, beeswarm plots, and explanation exports.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Loan XAI workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            key=NAVIGATION_SESSION_KEY,
        )
        st.caption("Data → Model → Explain → Export")

    PAGES[page]()
