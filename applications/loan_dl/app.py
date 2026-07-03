"""Loan Eligibility — Deep Learning application entry point."""

import streamlit as st
from core.launcher import go_home

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
    if st.button("← Platform home"):
        go_home()
        st.rerun()

    st.markdown(
        """
        <section class="aiew-loan-hero">
            <div class="aiew-app-icon" style="font-size:.6rem;">DL</div>
            <div>
                <h1>Loan Eligibility Prediction</h1>
                <p>
                    Deep learning workflow · multi-layer perceptron, loss curve,
                    full evaluation suite, and in-memory artifact export.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Loan DL workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            key=NAVIGATION_SESSION_KEY,
        )
        st.caption("Data → Features → Network → Evaluation")

    PAGES[page]()
