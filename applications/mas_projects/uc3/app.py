"""MAS Projects — UC3: Debate & Judge entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.mas_projects.uc3.constants import NAVIGATION_SESSION_KEY
from applications.mas_projects.uc3.pages import configure, history, setup
from applications.mas_projects.uc3.pages import run as run_page


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
        <section class="aiew-tier-banner aiew-tb--t3">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC3</div>
                <div>
                    <div class="aiew-tb-cap">MAS Projects · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Debate &amp; Judge</div>
                    <div class="aiew-tb-desc">
                        Two adversarial agents argue opposing positions on any topic
                        across multiple rounds. A neutral Judge then evaluates the
                        quality of both arguments and declares a winner with reasoning.
                    </div>
                    <div class="aiew-tb-flow">🟦 Proponent → 🟥 Opponent → 🟦 → 🟥 → ⚖️ Judge</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Adversarial Pattern</span>
                        <span class="aiew-tech-pill">Conditional Routing</span>
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
                "The Proponent and Opponent agents argue back and forth for N rounds. "
                "Neither agent has a goal to be accurate — only to be persuasive. "
                "The Judge reads the full debate and evaluates based on logic and evidence."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC3** introduces Adversarial MAS: agents with opposing objectives. "
                "This pattern surfaces trade-offs and hidden assumptions that a single "
                "agent or cooperative team might miss. The Judge provides grounded closure."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Framework", "Pattern", "Agent A", "Agent B", "Arbitrator", "Routing"],
                "Technology": [
                    "LangGraph StateGraph",
                    "Adversarial / deliberative",
                    "Proponent — argues FOR",
                    "Opponent — argues AGAINST",
                    "Judge — evaluates & decides",
                    "Conditional edge (rounds counter)",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Debate &amp; Judge · UC3 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("🟦 Proponent  ·  🟥 Opponent  ·  ⚖️ Judge")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
