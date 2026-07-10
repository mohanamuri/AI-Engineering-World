"""
UC1 — Setup page.

Users select which tools the ReAct agent can use and optionally override
the system prompt. Stores an AgentSetup dict to session state.
"""

import streamlit as st

from applications.agent_projects.uc1.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant that reasons step-by-step and uses tools "
    "when needed. Always think before acting. After using a tool, incorporate "
    "the result into your reasoning before deciding the next step."
)

_TOOL_INFO = {
    "calculator": {
        "label": "🧮 Calculator",
        "desc": "Evaluates math expressions safely using Python's ast module. "
                "Supports +, -, *, /, **, %, //.",
    },
    "wikipedia": {
        "label": "📖 Wikipedia",
        "desc": "Looks up factual information via the Wikipedia REST API. "
                "Returns a concise summary paragraph.",
    },
}

_SAMPLE_TASKS = [
    "What is the population of Japan and how does it compare to Germany?",
    "Calculate the compound interest on $5000 at 7% annual rate for 10 years.",
    "What is Python and what is it primarily used for?",
    "How many seconds are in a year? Show your calculation.",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})

    st.markdown("#### Available tools")
    st.caption(
        "Select which tools the ReAct agent can call. "
        "The agent decides autonomously when and how to use each one."
    )

    enabled_tools: list[str] = []
    cols = st.columns(len(_TOOL_INFO))
    defaults = setup.get("enabled_tools", list(_TOOL_INFO.keys()))

    for col, (tool_name, meta) in zip(cols, _TOOL_INFO.items()):
        with col:
            with st.container(border=True):
                checked = st.checkbox(
                    meta["label"],
                    value=(tool_name in defaults),
                    key=f"uc1_tool_{tool_name}",
                )
                st.caption(meta["desc"])
                if checked:
                    enabled_tools.append(tool_name)

    st.markdown("#### System prompt")
    st.caption("Optional: customise the agent's persona and instructions.")
    system_prompt = st.text_area(
        "System prompt",
        value=setup.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        height=100,
        label_visibility="collapsed",
        key="uc1_system_prompt",
    )

    if st.button("💾 Save Setup", use_container_width=False):
        if not enabled_tools:
            st.warning("Select at least one tool before saving.")
        else:
            st.session_state[AGENT_SETUP_SESSION_KEY] = {
                "enabled_tools": enabled_tools,
                "system_prompt": system_prompt,
            }
            st.success("Setup saved. Head to **Configure** to tune model parameters.")

    st.divider()
    st.markdown("#### Sample tasks to try")
    for q in _SAMPLE_TASKS:
        st.caption(f"• {q}")
