"""Prompt Engineering — UC1: Zero-shot vs Few-shot entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.prompt_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.prompt_projects.uc1.pages import compare, concept, insights, playground


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
                    <div class="aiew-tb-cap">Prompt Engineering · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">Zero-shot vs Few-shot</div>
                    <div class="aiew-tb-desc">
                        See exactly how adding examples to your prompt changes the output.
                        Zero-shot asks the LLM cold; few-shot primes it with 2–3 demonstrations.
                        Run both on the same task and compare quality side by side.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">meta-llama/llama-4-scout-17b-16e-instruct</span>
                        <span class="aiew-tech-pill">Zero-shot</span>
                        <span class="aiew-tech-pill">Few-shot</span>
                        <span class="aiew-tech-pill">Prompt Design</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Zero-shot vs Few-shot · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
