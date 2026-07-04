import streamlit as st
from core.launcher import go_home

from applications.hr_ml.constants import (
    NAVIGATION_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.hr_ml.pages import (
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
                    <div class="aiew-tb-title">HR Analytics — Employee Attrition Prediction</div>
                    <div class="aiew-tb-desc">
                        Classical ML pipeline on an HR Attrition dataset — explore workforce signals,
                        preprocess features, train four classifiers, evaluate with F1 and ROC AUC,
                        and export a deployment-ready artifact bundle.
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
        st.markdown('<div class="aiew-side-label">HR Analytics · T1 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload IBM HR → Explore → Preprocess → Train → Evaluate → Export")

    PAGES[page]()
