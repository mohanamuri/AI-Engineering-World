"""MAS Projects — UC4: Research Team entry point."""

import streamlit as st
from core.launcher import go_home

from applications.mas_projects.uc4.constants import NAVIGATION_SESSION_KEY
from applications.mas_projects.uc4.pages import configure, history, setup
from applications.mas_projects.uc4.pages import run as run_page


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
        <section class="aiew-tier-banner aiew-tb--t4">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">MAS Projects · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Research Team</div>
                    <div class="aiew-tb-desc">
                        A full four-agent research crew: Planner breaks the query into
                        research questions, Researcher looks up each one (Wikipedia),
                        Analyst synthesises all findings, Writer produces the final report.
                        Memory accumulates across every stage.
                    </div>
                    <div class="aiew-tb-flow">📋 Plan → 🔎 Research × N → 📊 Analyse → 📝 Write</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq llama-3.3-70b</span>
                        <span class="aiew-tech-pill">Iterative Research</span>
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
                "The most capable MAS pattern on the platform. The Planner decomposes "
                "any complex query into focused research questions. The Researcher "
                "answers each one with Wikipedia. The Analyst synthesises. The Writer "
                "produces a comprehensive, structured report."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC4** introduces iterative research with memory: the Researcher "
                "node is called once per question in a loop, accumulating findings "
                "before passing everything to the Analyst. This mirrors how real "
                "research teams operate."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Framework", "Pattern", "Agent 1", "Agent 2", "Agent 3", "Agent 4"],
                "Technology": [
                    "LangGraph StateGraph",
                    "Multi-role pipeline with iterative loop",
                    "Planner — breaks query into questions",
                    "Researcher — Wikipedia lookup per question",
                    "Analyst — synthesises all findings",
                    "Writer — final comprehensive report",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Research Team · UC4 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("📋 Plan  ·  🔎 Research  ·  📊 Analyse  ·  📝 Write")

    PAGES[page]()
