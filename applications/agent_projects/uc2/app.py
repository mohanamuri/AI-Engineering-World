"""Agent Projects — UC2: Plan-and-Execute Agent entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.agent_projects.uc2.constants import NAVIGATION_SESSION_KEY
from applications.agent_projects.uc2.pages import concept, configure, history, setup
from applications.agent_projects.uc2.pages import run as run_page


PAGES = {
    "📖 Concept":  concept.render,
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
                    <div class="aiew-tb-cap">Agent Projects · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">Plan-and-Execute Agent</div>
                    <div class="aiew-tb-desc">
                        Before acting, the agent creates a numbered multi-step plan.
                        An executor then runs each step in order — calling tools where needed —
                        and a responder synthesises all results into a final answer.
                    </div>
                    <div class="aiew-tb-flow">🛠️ Setup → 📝 Plan → 🔄 Execute each step → 📊 Synthesise → ✅ Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Planner LLM</span>
                        <span class="aiew-tech-pill">Wikipedia API</span>
                        <span class="aiew-tech-pill">Calculator</span>
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
                "UC1's ReAct agent decides what to do one step at a time — "
                "reactive, no upfront plan."
            )
            st.write(
                "UC2 separates **planning** from **execution**. "
                "First, the LLM creates a complete numbered plan for the task. "
                "Then an executor works through each step, calling tools as needed. "
                "Finally, a responder synthesises every step result into a coherent answer."
            )
            st.markdown("#### New concept over UC1")
            st.info(
                "**UC1** reacts one step at a time (no global view).\n\n"
                "**UC2** creates a full plan upfront — the executor knows the whole task "
                "structure before taking the first action. This makes multi-step reasoning "
                "more transparent and prevents the agent from going off-track mid-task."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": [
                    "Agent framework",
                    "Planning node",
                    "Execution node",
                    "Synthesis node",
                    "Tools",
                    "LLM",
                ],
                "Technology": [
                    "LangGraph StateGraph",
                    "Groq LLM — generates numbered plan",
                    "Loop over plan steps; auto-picks tool per step",
                    "Groq LLM — combines step results",
                    "Calculator (ast-safe) · Wikipedia REST API",
                    "Groq compound-beta-mini",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Plan-Execute · UC2 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("📝 Plan  ·  🔄 Execute  ·  📊 Synthesise")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
