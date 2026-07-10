"""Prompt Engineering — UC3: Structured Output entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.prompt_projects.uc3.constants import NAVIGATION_SESSION_KEY
from applications.prompt_projects.uc3.pages import compare, concept, insights, playground


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
        <section class="aiew-tier-banner aiew-tb--t3">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC3</div>
                <div>
                    <div class="aiew-tb-cap">Prompt Engineering · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Structured Output</div>
                    <div class="aiew-tb-desc">
                        Force the model to return machine-readable JSON every time.
                        Structured output bridges the gap between LLM text generation and
                        downstream code that needs reliable, parseable data.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">llama-3.1-8b-instant</span>
                        <span class="aiew-tech-pill">JSON Schema</span>
                        <span class="aiew-tech-pill">Structured Output</span>
                        <span class="aiew-tech-pill">Parsing</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Structured Output · UC3 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
