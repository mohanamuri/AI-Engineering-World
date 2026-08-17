"""Prompt Engineering — UC4: Prompt Chaining entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.prompt_projects.uc4.constants import NAVIGATION_SESSION_KEY
from applications.prompt_projects.uc4.pages import compare, concept, insights, playground


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
        <section class="aiew-tier-banner aiew-tb--t4">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">Prompt Engineering · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Prompt Chaining</div>
                    <div class="aiew-tb-desc">
                        Break complex tasks into a sequence of smaller prompts —
                        Outline → Draft → Refine. Each step's output feeds the next.
                        Compare quality against a single monolithic prompt on the same task.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">llama-3.3-70b-versatile</span>
                        <span class="aiew-tech-pill">Prompt Chaining</span>
                        <span class="aiew-tech-pill">Decomposition</span>
                        <span class="aiew-tech-pill">Pipeline</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Prompt Chaining · UC4 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
