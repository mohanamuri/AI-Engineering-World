"""UC2 — Configure page: Parallel Agents."""

import streamlit as st

from applications.mas_projects.services.parallel_agents import ParallelAgentsConfig
from applications.mas_projects.uc2.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
)

_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
]


def render() -> None:
    st.subheader("⚙️ Configure")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: ParallelAgentsConfig = st.session_state.get(
        AGENT_CONFIG_SESSION_KEY, ParallelAgentsConfig()
    )

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model (all agents use the same model)",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="mas_uc2_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="mas_uc2_temperature",
            help="Slightly higher temperature (0.2–0.4) produces more diverse perspectives.",
        )
    with col2:
        st.info(
            "Higher temperature encourages each specialist to produce distinctly "
            "different outputs — which makes the aggregation more valuable."
        )

    with st.expander("How does the Fan-out / Fan-in pattern work?", expanded=False):
        st.markdown(
            "The three specialist agents (Facts, Critic, Creative) are **independent**: "
            "they each receive only the original task, with no knowledge of what the "
            "others are doing.\n\n"
            "The Aggregator then reads all three outputs simultaneously and synthesises "
            "a richer answer than any single agent could produce alone.\n\n"
            "| Parameter | Effect |\n"
            "|---|---|\n"
            "| LLM model | Same model used across all 4 agents |\n"
            "| Temperature | Low = precise · Higher = more diverse perspectives |"
        )

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = ParallelAgentsConfig(
            llm_model=model,
            temperature=temperature,
            system_prompt=setup.get("system_prompt", ParallelAgentsConfig().system_prompt),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to execute the agent team.")
