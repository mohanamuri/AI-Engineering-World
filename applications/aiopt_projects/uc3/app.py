"""AI Optimisation Techniques — UC3: Memory Patterns entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.aiopt_projects.uc3.constants import NAVIGATION_SESSION_KEY
from applications.aiopt_projects.uc3.pages import compare, concept, insights, playground
from applications.aiopt_projects.services.tier_guide import render as tier_guide


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
                <div class="aiew-tier-badge-lg">UC3</div>
                <div>
                    <div class="aiew-tb-cap">AI Optimisation Techniques · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Memory Patterns</div>
                    <div class="aiew-tb-desc">
                        Multi-turn conversations need memory management. Compare three strategies:
                        Buffer (keep last N messages), Summary (compress old turns), and Entity
                        (extract facts and maintain a knowledge store across the conversation).
                    </div>
                    <div class="aiew-tb-flow">📖 Concept → 🧪 Playground → ⚖️ Compare → 💡 Insights</div>
                    <div>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Buffer Memory</span>
                        <span class="aiew-tech-pill">Summary Memory</span>
                        <span class="aiew-tech-pill">Entity Memory</span>
                        <span class="aiew-tech-pill">Context Management</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Memory Patterns · UC3 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Concept → Playground → Compare → Insights")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
