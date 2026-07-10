"""
UC4 — Setup page.

The Multi-Agent Supervisor has three fixed specialist agents
(Researcher, Analyst, Writer). This page explains the team structure
and lets users customise the system prompt.
"""

import streamlit as st

from applications.agent_projects.uc4.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_SYSTEM_PROMPT = (
    "You are coordinating a team of specialist AI agents. "
    "Each specialist will contribute their expertise. "
    "The final answer should be accurate, well-structured, and complete."
)

_AGENTS = [
    {
        "name": "🔍 Researcher",
        "role": "Looks up factual information using the Wikipedia API. "
                "Called when the task needs encyclopaedic knowledge.",
        "tool": "Wikipedia",
    },
    {
        "name": "🧮 Analyst",
        "role": "Performs numerical calculations using the safe Calculator. "
                "Called when the task requires quantitative reasoning.",
        "tool": "Calculator",
    },
    {
        "name": "✍️ Writer",
        "role": "Synthesises all findings into a polished final answer. "
                "Called last to produce the response the user sees.",
        "tool": "None (pure LLM)",
    },
]

_SAMPLE_TASKS = [
    "What is the population of Tokyo and how does it compare to New York?",
    "Research machine learning and estimate how many parameters GPT-3 has in billions.",
    "What is the speed of light and how long does it take light to travel from Earth to Mars?",
    "Explain blockchain technology and calculate how many hashes are in 2^256.",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})

    st.markdown("#### Agent team")
    st.caption("Three fixed specialist agents — the Supervisor decides who acts next.")

    cols = st.columns(len(_AGENTS))
    for col, agent in zip(cols, _AGENTS):
        with col:
            with st.container(border=True):
                st.markdown(f"**{agent['name']}**")
                st.caption(agent["role"])
                st.caption(f"Tool: `{agent['tool']}`")

    st.markdown("#### Supervisor system prompt")
    st.caption("Customise how the supervisor coordinates the team.")
    system_prompt = st.text_area(
        "System prompt",
        value=setup.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        height=100,
        label_visibility="collapsed",
        key="uc4_system_prompt",
    )

    if st.button("💾 Save Setup", use_container_width=False):
        st.session_state[AGENT_SETUP_SESSION_KEY] = {"system_prompt": system_prompt}
        st.success("Setup saved. Head to **Configure** to tune model parameters.")

    st.divider()
    st.markdown("#### Sample tasks to try")
    for q in _SAMPLE_TASKS:
        st.caption(f"• {q}")
