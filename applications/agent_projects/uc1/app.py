"""Agent Projects — UC1: ReAct Agent entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.agent_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.agent_projects.uc1.pages import concept, configure, history, setup
from applications.agent_projects.uc1.pages import run as run_page


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
        <section class="aiew-tier-banner aiew-tb--t1">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC1</div>
                <div>
                    <div class="aiew-tb-cap">Agent Projects · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">ReAct Agent</div>
                    <div class="aiew-tb-desc">
                        The classic Reason+Act loop: the LLM reasons about what to do,
                        calls a tool, observes the result, and reasons again — cycling
                        until it has enough information to answer. Every step is visible.
                    </div>
                    <div class="aiew-tb-flow">🛠️ Setup → ⚙️ Configure → 🤔 Reason → 🔧 Act → 📋 Observe → ✅ Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Tool Calling</span>
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
                "A ReAct agent wraps an LLM with a small set of tools and lets it "
                "decide, at each step, whether to call a tool or produce a final answer."
            )
            st.write(
                "The key innovation is the **reasoning trace** — every tool call "
                "and every LLM decision is captured and shown, so you can see exactly "
                "how the agent reached its answer. There is no black box."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC1** is where agents begin. The agent uses tools — "
                "something a plain LLM cannot do. The ReAct loop "
                "(Reason → Act → Observe → Reason…) is the foundation "
                "that all more advanced agent patterns build on."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": [
                    "Agent framework",
                    "Loop pattern",
                    "Tool interface",
                    "Tools available",
                    "LLM",
                ],
                "Technology": [
                    "LangGraph StateGraph",
                    "agent_node ↔ tools_node cycle",
                    "Groq native tool-calling API",
                    "Calculator (ast-safe) · Wikipedia REST API",
                    "Groq gemma2-9b-it",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">ReAct Agent · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("🤔 Reason  ·  🔧 Act  ·  📋 Observe")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
