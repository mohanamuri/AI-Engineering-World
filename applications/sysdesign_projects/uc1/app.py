"""System Design at Scale — UC1: Latency Budget entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.sysdesign_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.sysdesign_projects.uc1.pages import compare, concept, insights, playground
from applications.sysdesign_projects.services.tier_guide import render as tier_guide


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
                    <div class="aiew-tb-cap">System Design · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">Latency Budget</div>
                    <div class="aiew-tb-desc">
                        Waterfall breakdown — where does the time go?
                        Understand the latency of each stage in a RAG + LLM request:
                        network, embedding, vector search, LLM TTFT, and generation.
                        See how streaming cuts perceived latency by 70–80%.
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Latency</span>
                        <span class="aiew-tech-pill">Waterfall</span>
                        <span class="aiew-tech-pill">TTFT</span>
                        <span class="aiew-tech-pill">Streaming</span>
                        <span class="aiew-tech-pill">Plotly</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">System Design · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
