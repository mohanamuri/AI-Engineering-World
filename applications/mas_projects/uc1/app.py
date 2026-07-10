"""MAS Projects — UC1: Supervisor Pipeline entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.mas_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.mas_projects.uc1.pages import configure, history, setup
from applications.mas_projects.uc1.pages import run as run_page


PAGES = {
    "🛠️ Setup":     setup.render,
    "⚙️ Configure": configure.render,
    "▶️ Run":        run_page.render,
    "📜 History":   history.render,
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
                    <div class="aiew-tb-cap">MAS Projects · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">Supervisor Pipeline</div>
                    <div class="aiew-tb-desc">
                        A fixed sequential pipeline where each agent's output feeds
                        directly into the next: Collector gathers facts, Processor
                        extracts insights, Writer drafts the response, Supervisor
                        closes with an executive summary.
                    </div>
                    <div class="aiew-tb-flow">🗂️ Collect → 🔬 Process → ✍️ Write → 🧭 Summarise</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Pipeline Pattern</span>
                        <span class="aiew-tech-pill">Wikipedia API</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("About this use case", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### What this use case does")
            st.write(
                "A Supervisor coordinates three specialist agents in a fixed sequence. "
                "Each agent receives the previous agent's output as its primary input — "
                "creating a chain where knowledge accumulates stage by stage."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC1** introduces the Pipeline pattern: a structured sequence where "
                "agents hand off enriched context rather than acting independently. "
                "Unlike dynamic routing, the flow is deterministic and auditable."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Framework", "Pattern", "Stage 1", "Stage 2", "Stage 3", "Stage 4"],
                "Technology": [
                    "LangGraph StateGraph",
                    "Sequential pipeline (A → B → C)",
                    "Collector — Wikipedia research",
                    "Processor — insight extraction",
                    "Writer — structured prose",
                    "Supervisor — executive summary",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Supervisor Pipeline · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("🗂️ Collect  ·  🔬 Process  ·  ✍️ Write  ·  🧭 Summarise")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
