"""UC3 — Configure page: Debate & Judge."""

import streamlit as st

from applications.mas_projects.services.debate_judge import DebateConfig
from applications.mas_projects.uc3.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
)

_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "gemma2-9b-it",
]


def render() -> None:
    st.subheader("⚙️ Configure")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: DebateConfig = st.session_state.get(
        AGENT_CONFIG_SESSION_KEY, DebateConfig()
    )

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model (all agents use the same model)",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="mas_uc3_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="mas_uc3_temperature",
            help="Higher temperature produces more varied and creative arguments.",
        )
    with col2:
        num_rounds = st.slider(
            "Number of debate rounds",
            min_value=1, max_value=3,
            value=config.num_rounds,
            step=1,
            key="mas_uc3_num_rounds",
            help="Each round = one Proponent argument + one Opponent argument.",
        )

    with st.expander("How does the Debate & Judge pattern work?", expanded=False):
        st.markdown(
            "The Proponent and Opponent alternate arguments. After each Opponent turn, "
            "a conditional edge checks whether the max rounds have been reached:\n\n"
            "- If more rounds remain → back to Proponent\n"
            "- If rounds exhausted → to Judge\n\n"
            "The Judge reads the **full debate history** and evaluates based on "
            "logic, evidence, and persuasion — then declares a winner.\n\n"
            "| Parameter | Effect |\n"
            "|---|---|\n"
            "| Temperature | Low = precise · Higher = more creative arguments |\n"
            "| Rounds | 1 = quick verdict · 3 = full debate with rebuttals |"
        )

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = DebateConfig(
            llm_model=model,
            temperature=temperature,
            num_rounds=num_rounds,
            proponent_persona=setup.get("proponent_persona", DebateConfig().proponent_persona),
            opponent_persona=setup.get("opponent_persona", DebateConfig().opponent_persona),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to start the debate.")
