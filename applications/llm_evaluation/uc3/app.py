"""LLM Evaluation — UC3: Hallucination Detection entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.llm_evaluation.uc3.constants import NAVIGATION_SESSION_KEY
from applications.llm_evaluation.uc3.pages import compare, concept, insights, playground
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
        <section class="aiew-tier-banner aiew-tb--t3">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC3</div>
                <div>
                    <div class="aiew-tb-cap">LLM Evaluation · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Hallucination Detection</div>
                    <div class="aiew-tb-desc">
                        Detect fabricated facts before they reach users.
                        Extract individual claims from LLM responses, verify each against
                        source context, and compute a hallucination rate with per-claim verdicts.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Claim Extraction</span>
                        <span class="aiew-tech-pill">NLI</span>
                        <span class="aiew-tech-pill">Hallucination Rate</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">LLM Evaluation · UC3 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
