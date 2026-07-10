"""MAS Projects — UC2: Parallel Agents entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.mas_projects.uc2.constants import NAVIGATION_SESSION_KEY
from applications.mas_projects.uc2.pages import configure, history, setup
from applications.mas_projects.uc2.pages import run as run_page


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
        <section class="aiew-tier-banner aiew-tb--t2">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC2</div>
                <div>
                    <div class="aiew-tb-cap">MAS Projects · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">Parallel Agents</div>
                    <div class="aiew-tb-desc">
                        Three independent specialist agents tackle the same task from
                        completely different angles — Facts, Critic, and Creative —
                        with no shared intermediate state. An Aggregator then merges
                        all three perspectives into one coherent response.
                    </div>
                    <div class="aiew-tb-flow">📊 Facts ⟳ 🔍 Critic ⟳ 💡 Creative → 🔀 Aggregate</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Fan-out / Fan-in</span>
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
                "Three agents independently analyse the same task. Each agent has no "
                "knowledge of what the others are doing. An Aggregator reads all three "
                "outputs and produces a richer answer than any single agent could."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC2** introduces Fan-out / Fan-in: one input distributed to N "
                "independent agents, N outputs merged into one. This pattern increases "
                "breadth and reduces blind spots compared to a single agent."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Framework", "Pattern", "Agent 1", "Agent 2", "Agent 3", "Final step"],
                "Technology": [
                    "LangGraph StateGraph",
                    "Fan-out / Fan-in",
                    "Facts Agent — Wikipedia facts",
                    "Critic Agent — challenges & risks",
                    "Creative Agent — novel angles",
                    "Aggregator — merges all three",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Parallel Agents · UC2 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("📊 Facts  ·  🔍 Critic  ·  💡 Creative  ·  🔀 Aggregate")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
