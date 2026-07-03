import streamlit as st
from core.launcher import go_home

from applications.loan_ml.constants import (
    NAVIGATION_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.loan_ml.pages import (
    upload,
    explore,
    preprocess,
    train,
    evaluate,
    download,
)


PAGES = {
    UPLOAD_PAGE_LABEL: upload.render,
    "📊 Explore Data": explore.render,
    "🧹 Preprocess": preprocess.render,
    "🤖 Train Model": train.render,
    "📈 Evaluate Model": evaluate.render,
    "⬇ Download Model": download.render,
}


def run():
    if st.button("← Platform home"):
        go_home()
        st.rerun()

    st.markdown(
        """
        <section class="aiew-loan-hero">
            <div class="aiew-app-icon">ML</div>
            <div>
                <h1>Loan Eligibility Prediction</h1>
                <p>
                    Production ML workflow · validate data, explore signals,
                    engineer features, train, evaluate, and export.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Loan ML workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            key=NAVIGATION_SESSION_KEY,
        )
        st.caption("Data → Features → Model → Evaluation")

    PAGES[page]()
