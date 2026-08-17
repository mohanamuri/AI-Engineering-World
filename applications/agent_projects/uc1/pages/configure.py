"""
UC1 — Configure page.

Tune model parameters for the ReAct agent.
"""

import streamlit as st

from applications.agent_projects.services.react_agent import ReactConfig
from applications.agent_projects.uc1.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
)

_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "gemma2-9b-it",
]


def render() -> None:
    st.subheader("⚙️ Configure")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first to select tools before configuring the agent.")
        return

    config: ReactConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, ReactConfig())

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="uc1_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="uc1_temperature",
            help="0 = deterministic, 1 = creative",
        )
    with col2:
        max_iterations = st.slider(
            "Max iterations",
            min_value=2, max_value=12,
            value=config.max_iterations,
            step=1,
            key="uc1_max_iter",
            help="Maximum number of agent → tool cycles before forcing a final answer.",
        )

        st.markdown("##### Active tools")
        for t in setup.get("enabled_tools", []):
            st.caption(f"✓ {t}")

    with st.expander("How does the ReAct loop work?", expanded=False):
        st.markdown(
            "The **ReAct** pattern interleaves two phases:\n\n"
            "1. **Reason** — the LLM reads the conversation history and decides what to do next "
            "(call a tool, or answer directly).\n"
            "2. **Act** — if a tool was chosen, it executes and the result is appended to the "
            "context. The agent then reasons again.\n\n"
            "This loop repeats until the LLM decides it has enough information to answer, "
            "or until **Max iterations** is reached."
        )
        st.table({
            "Parameter": ["LLM model", "Temperature", "Max iterations"],
            "Effect": [
                "Larger models reason better but are slower",
                "Low = consistent · High = creative",
                "More iterations = more tool calls = richer answers (but slower)",
            ],
        })

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = ReactConfig(
            llm_model=model,
            temperature=temperature,
            max_iterations=max_iterations,
            enabled_tools=setup.get("enabled_tools", ["calculator", "wikipedia"]),
            system_prompt=setup.get("system_prompt", ReactConfig().system_prompt),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to execute the agent.")
