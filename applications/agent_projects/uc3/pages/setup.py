"""
UC3 — Setup page.

The Reflection agent doesn't use external tools — it only needs a
system prompt and task instructions. This page lets users customise
the agent's persona and see sample tasks.
"""

import streamlit as st

from applications.agent_projects.uc3.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_SYSTEM_PROMPT = (
    "You are a thoughtful writer who produces clear, accurate, and complete responses. "
    "When given feedback, you revise your work to address every critique point specifically."
)

_SAMPLE_TASKS = [
    "Explain the difference between supervised and unsupervised learning.",
    "Write a brief explanation of how transformer models work.",
    "Describe the key principles of clean code in software engineering.",
    "Explain what gradient descent is and how it's used in machine learning.",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})

    st.markdown("#### No external tools")
    st.info(
        "The Reflection agent is **tool-free** — it relies entirely on the LLM's "
        "own reasoning ability. The quality improvement comes from the self-critique "
        "loop, not from external data sources."
    )

    st.markdown("#### System prompt")
    st.caption("Customise the agent's writing style and revision behaviour.")
    system_prompt = st.text_area(
        "System prompt",
        value=setup.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        height=110,
        label_visibility="collapsed",
        key="uc3_system_prompt",
    )

    if st.button("💾 Save Setup", use_container_width=False):
        st.session_state[AGENT_SETUP_SESSION_KEY] = {"system_prompt": system_prompt}
        st.success("Setup saved. Head to **Configure** to tune quality thresholds.")

    st.divider()
    st.markdown("#### Sample tasks to try")
    for q in _SAMPLE_TASKS:
        st.caption(f"• {q}")
