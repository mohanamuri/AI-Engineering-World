"""
UC2 — Setup page.

Users select tools and optionally customise the system prompt
for the Plan-and-Execute agent.
"""

import streamlit as st

from applications.agent_projects.uc2.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_SYSTEM_PROMPT = (
    "You are a methodical assistant that breaks complex tasks into clear steps, "
    "executes each step using available tools, and synthesises results into "
    "a well-structured final answer."
)

_TOOL_INFO = {
    "calculator": {
        "label": "🧮 Calculator",
        "desc": "Evaluates math expressions for quantitative steps in the plan.",
    },
    "wikipedia": {
        "label": "📖 Wikipedia",
        "desc": "Looks up factual information for research steps in the plan.",
    },
}

_SAMPLE_TASKS = [
    "Compare the GDP of the USA, China, and Germany, then rank them.",
    "Explain quantum computing and calculate how many qubits are in 2^10.",
    "What is climate change and what are three key statistics about it?",
    "Research the history of the internet and summarise its five key milestones.",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})
    defaults = setup.get("enabled_tools", list(_TOOL_INFO.keys()))

    st.markdown("#### Available tools")
    st.caption("The executor will automatically pick the right tool for each plan step.")

    enabled_tools: list[str] = []
    cols = st.columns(len(_TOOL_INFO))
    for col, (tool_name, meta) in zip(cols, _TOOL_INFO.items()):
        with col:
            with st.container(border=True):
                checked = st.checkbox(
                    meta["label"],
                    value=(tool_name in defaults),
                    key=f"uc2_tool_{tool_name}",
                )
                st.caption(meta["desc"])
                if checked:
                    enabled_tools.append(tool_name)

    st.markdown("#### System prompt")
    system_prompt = st.text_area(
        "System prompt",
        value=setup.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        height=100,
        label_visibility="collapsed",
        key="uc2_system_prompt",
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
