"""Prompt Engineering — UC2: Chain-of-Thought entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.prompt_projects.uc2.constants import NAVIGATION_SESSION_KEY
from applications.prompt_projects.uc2.pages import compare, concept, insights, playground


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
        <section class="aiew-tier-banner aiew-tb--t2">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC2</div>
                <div>
                    <div class="aiew-tb-cap">Prompt Engineering · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">Chain-of-Thought Prompting</div>
                    <div class="aiew-tb-desc">
                        Adding "Let's think step by step" unlocks the model's reasoning ability.
                        CoT dramatically improves accuracy on logic, math, and multi-step problems
                        by making the model show its work before answering.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">mixtral-8x7b-32768</span>
                        <span class="aiew-tech-pill">Chain-of-Thought</span>
                        <span class="aiew-tech-pill">Reasoning</span>
                        <span class="aiew-tech-pill">Step-by-step</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Chain-of-Thought · UC2 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
