"""AI Optimisation Techniques — UC2: Model Routing entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.aiopt_projects.uc2.constants import NAVIGATION_SESSION_KEY
from applications.aiopt_projects.uc2.pages import compare, concept, insights, playground


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
                <div class="aiew-tier-badge-lg">UC2</div>
                <div>
                    <div class="aiew-tb-cap">AI Optimisation Techniques · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">Model Routing</div>
                    <div class="aiew-tb-desc">
                        A lightweight classifier reads each query and decides which model to use.
                        Simple tasks go to the fast 8B model; complex tasks go to the powerful 70B.
                        Reduce cost by 60–80 % without sacrificing quality where it matters.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">llama-3.3-70b-versatile</span>
                        <span class="aiew-tech-pill">llama-3.3-70b-versatile</span>
                        <span class="aiew-tech-pill">Complexity Classifier</span>
                        <span class="aiew-tech-pill">Cost Optimisation</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Model Routing · UC2 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
