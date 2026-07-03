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
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t1">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">T1</div>
                <div>
                    <div class="aiew-tb-cap">Machine Learning · Tier 1 of 6</div>
                    <div class="aiew-tb-title">Loan Eligibility Prediction</div>
                    <div class="aiew-tb-desc">
                        Production ML workflow — validate data, explore signals, engineer features,
                        train classical models, evaluate rigorously, and export a deployment bundle.
                    </div>
                    <div class="aiew-tb-flow">📤 Upload → 📊 Explore → 🧹 Preprocess → 🤖 Train → 📈 Evaluate → ⬇ Export</div>
                    <div>
                        <span class="aiew-tech-pill">scikit-learn</span>
                        <span class="aiew-tech-pill">XGBoost</span>
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
        st.markdown('<div class="aiew-side-label">Loan ML · T1 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Data → Features → Model → Evaluation")

    PAGES[page]()
