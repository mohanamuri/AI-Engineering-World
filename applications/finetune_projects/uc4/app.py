"""Fine-tuning Techniques — UC4: Instruction Tuning entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.finetune_projects.uc4.constants import NAVIGATION_SESSION_KEY
from applications.finetune_projects.uc4.pages import compare, concept, insights, playground
from applications.finetune_projects.services.tier_guide import render as tier_guide


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
        <section class="aiew-tier-banner aiew-tb--t4">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">Fine-tuning · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Instruction Tuning</div>
                    <div class="aiew-tb-desc">
                        Alpaca · ChatML · ShareGPT dataset formats.
                        Learn how to structure instruction-following datasets,
                        understand the difference between the three main formats,
                        and apply the data quality checklist before training.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Instruction Tuning</span>
                        <span class="aiew-tech-pill">Alpaca</span>
                        <span class="aiew-tech-pill">ChatML</span>
                        <span class="aiew-tech-pill">Dataset Formats</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Fine-tuning · UC4 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
