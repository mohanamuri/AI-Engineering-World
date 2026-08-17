"""Agent Projects — UC4: Multi-Agent Supervisor entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.agent_projects.uc4.constants import NAVIGATION_SESSION_KEY
from applications.agent_projects.uc4.pages import concept, configure, history, setup
from applications.agent_projects.uc4.pages import run as run_page


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
        <section class="aiew-tier-banner aiew-tb--t6">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">Agent Projects · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Multi-Agent Supervisor</div>
                    <div class="aiew-tb-desc">
                        A Supervisor LLM reads the task and routes work to specialist agents:
                        a Researcher (Wikipedia), an Analyst (Calculator), and a Writer.
                        After each specialist acts, the Supervisor decides whether more work
                        is needed — until the Writer produces the final answer.
                    </div>
                    <div class="aiew-tb-flow">🧭 Supervise → 🔍 Research | 🧮 Analyse → 🧭 Re-evaluate → ✍️ Write → ✅ Done</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Supervisor Pattern</span>
                        <span class="aiew-tech-pill">Wikipedia API</span>
                        <span class="aiew-tech-pill">Calculator</span>
                        <span class="aiew-tech-pill">3 Specialist Agents</span>
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
                "UC1–UC3 each use a single LLM as the agent — one entity doing everything."
            )
            st.write(
                "UC4 introduces a **team of agents**, each with a distinct role. "
                "A Supervisor LLM reads the task and decides which specialist to call: "
                "the Researcher (Wikipedia lookup), the Analyst (Calculator), "
                "or the Writer (final synthesis). After each specialist acts, "
                "the Supervisor re-evaluates whether more work is needed."
            )
            st.markdown("#### New concept over UC3")
            st.info(
                "**UC3** is one agent critiquing its own work — still a solo actor.\n\n"
                "**UC4** splits cognition across multiple agents. Each specialist "
                "only does one thing well. The Supervisor provides coordination without "
                "doing the actual work. This mirrors real team dynamics: "
                "a manager directs, specialists execute."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": [
                    "Agent framework",
                    "Supervisor",
                    "Researcher agent",
                    "Analyst agent",
                    "Writer agent",
                    "Routing",
                    "LLM",
                ],
                "Technology": [
                    "LangGraph StateGraph",
                    "Groq LLM — routes to researcher/analyst/writer/FINISH",
                    "Wikipedia REST API lookup",
                    "ast-safe Calculator",
                    "Groq LLM — synthesises final answer",
                    "Structured output: single-word decision per round",
                    "Groq llama-3.3-70b-versatile",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Multi-Agent · UC4 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("🧭 Supervisor  ·  🔍 Researcher  ·  🧮 Analyst  ·  ✍️ Writer")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
