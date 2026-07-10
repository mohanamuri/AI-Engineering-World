"""Agent Projects — UC3: Reflection Agent entry point."""

import streamlit as st
from core.launcher import go_home

from applications.agent_projects.uc3.constants import NAVIGATION_SESSION_KEY
from applications.agent_projects.uc3.pages import configure, history, setup
from applications.agent_projects.uc3.pages import run as run_page


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
                    <div class="aiew-tb-cap">Agent Projects · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Reflection Agent</div>
                    <div class="aiew-tb-desc">
                        The agent writes a draft, then acts as its own critic — scoring
                        Clarity, Accuracy, and Completeness (1–5 each). Low scores trigger
                        a targeted rewrite. The loop repeats until quality passes or
                        max revisions is reached.
                    </div>
                    <div class="aiew-tb-flow">🛠️ Setup → ✍️ Generate → 🔍 Critique → 🔄 Revise if needed → ✅ Final</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Self-Critique</span>
                        <span class="aiew-tech-pill">Quality Loop</span>
                        <span class="aiew-tech-pill">No External Tools</span>
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
                "UC1 and UC2 both produce an answer and stop — neither one asks "
                "whether the answer is actually good."
            )
            st.write(
                "UC3 adds a **self-critique step** after every draft. "
                "The LLM reads its own output and scores it on three dimensions: "
                "Is it clearly written? Is it factually accurate? Is anything missing? "
                "Scores below the threshold trigger a targeted rewrite — and you can "
                "see every draft alongside its scores."
            )
            st.markdown("#### New concept over UC2")
            st.info(
                "**UC2** executes a plan with external tools — it doesn't evaluate output quality.\n\n"
                "**UC3** has no external tools at all. The improvement comes entirely from "
                "the LLM critiquing and rewriting its own work. "
                "This mirrors the Self-RAG concept applied to general-purpose generation."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": [
                    "Agent framework",
                    "Generator node",
                    "Critic node",
                    "Loop termination",
                    "Critique dimensions",
                    "LLM",
                ],
                "Technology": [
                    "LangGraph StateGraph",
                    "Groq LLM — writes or revises draft",
                    "Groq LLM — scores 3 dimensions 1–5",
                    "All scores ≥ threshold OR max revisions reached",
                    "Clarity · Accuracy · Completeness",
                    "Groq llama-3.1-8b-instant",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Reflection Agent · UC3 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Setup → Configure → Run → History")
        st.divider()
        st.caption("🟢 Pass  ·  🟡 Borderline  ·  🔴 Fail")

    PAGES[page]()
