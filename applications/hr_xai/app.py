import streamlit as st
from core.launcher import go_home

from applications.hr_xai.constants import NAVIGATION_SESSION_KEY, UPLOAD_PAGE_LABEL
from applications.hr_xai.pages import upload, explore, preprocess, train, explain, download


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
                    <div class="aiew-tb-title">HR Analytics — Explainable Attrition Predictions</div>
                    <div class="aiew-tb-desc">
                        Train an attrition classifier, then explain every prediction
                        globally and locally using SHAP and LIME. Understand
                        exactly why the model flags each employee as a flight risk.
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
        st.markdown('<div class="aiew-side-label">HR Analytics · T3 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Train → Explain → Export")

    PAGES[page]()
