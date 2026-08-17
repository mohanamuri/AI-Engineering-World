"""LLM Evaluation — UC2: LLM-as-Judge entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.llm_evaluation.uc2.constants import NAVIGATION_SESSION_KEY
from applications.llm_evaluation.uc2.pages import compare, concept, insights, playground
from applications.llm_evaluation.services.tier_guide import render as tier_guide


PAGES = {
    "📋 Tier Guide":  tier_guide,
    "📖 Concept":    concept.render,
    "🧪 Playground": playground.render,
    "⚖️ Compare":    compare.render,
    "💡 Insights":   insights.render,
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
                <div class="aiew-tier-badge-lg">UC2</div>
                <div>
                    <div class="aiew-tb-cap">LLM Evaluation · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">LLM-as-Judge</div>
                    <div class="aiew-tb-desc">
                        Use a second LLM to score responses on custom criteria — no human labellers needed.
                        Define rubrics for accuracy, clarity, completeness, and more.
                        Get 1–10 scores with reasoned explanations for every response.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">LLM Judge</span>
                        <span class="aiew-tech-pill">Criteria Scoring</span>
                        <span class="aiew-tech-pill">Pairwise Comparison</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">LLM Evaluation · UC2 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
