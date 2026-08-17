"""Fine-tuning Techniques — UC1: Fine-tune vs RAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.finetune_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.finetune_projects.uc1.pages import compare, concept, insights, playground
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
        <section class="aiew-tier-banner aiew-tb--t1">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC1</div>
                <div>
                    <div class="aiew-tb-cap">Fine-tuning · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">Fine-tune vs RAG</div>
                    <div class="aiew-tb-desc">
                        Decision framework — when to choose each approach.
                        Use a rule-based engine to evaluate your scenario across data availability,
                        task type, latency requirements, and budget — and get a
                        reasoned recommendation with pros, cons, and when to reconsider.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Decision Framework</span>
                        <span class="aiew-tech-pill">Rule Tree</span>
                        <span class="aiew-tech-pill">Fine-tune</span>
                        <span class="aiew-tech-pill">RAG</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Fine-tuning · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
