"""AI Optimisation Techniques — UC1: Semantic Caching entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.aiopt_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.aiopt_projects.uc1.pages import compare, concept, insights, playground


PAGES = {
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
                    <div class="aiew-tb-cap">AI Optimisation Techniques · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">Semantic Caching</div>
                    <div class="aiew-tb-desc">
                        Skip the LLM entirely when a similar question was already answered.
                        Embed queries, find the closest cached response above a similarity
                        threshold, and return it instantly — reducing cost and latency in one move.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">sentence-transformers</span>
                        <span class="aiew-tech-pill">Cosine Similarity</span>
                        <span class="aiew-tech-pill">Vector Cache</span>
                        <span class="aiew-tech-pill">llama-3.1-8b-instant</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Semantic Caching · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
