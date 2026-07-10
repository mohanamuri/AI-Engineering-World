"""AI Optimisation Techniques — UC4: Streaming + Fallback entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.aiopt_projects.uc4.constants import NAVIGATION_SESSION_KEY
from applications.aiopt_projects.uc4.pages import compare, concept, insights, playground


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
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">AI Optimisation Techniques · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Streaming + Fallback</div>
                    <div class="aiew-tb-desc">
                        Two production resilience patterns in one: Streaming returns tokens as they
                        generate — perceived latency drops dramatically. Fallback retries the primary
                        model then switches to a backup automatically. Essential for reliable LLM APIs.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Token Streaming</span>
                        <span class="aiew-tech-pill">Retry + Backoff</span>
                        <span class="aiew-tech-pill">Model Fallback</span>
                        <span class="aiew-tech-pill">Resilience</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Streaming + Fallback · UC4 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
