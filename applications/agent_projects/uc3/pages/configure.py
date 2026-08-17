"""UC3 — Configure page."""

import streamlit as st

from applications.agent_projects.services.reflection_agent import ReflectionConfig
from applications.agent_projects.uc3.constants import (
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

    config: ReflectionConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, ReflectionConfig())

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="uc3_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="uc3_temperature",
            help="Higher temperature encourages more diverse revision attempts.",
        )
    with col2:
        max_revisions = st.slider(
            "Max revisions",
            min_value=1, max_value=5,
            value=config.max_revisions,
            step=1,
            key="uc3_max_revisions",
            help="Maximum number of draft → critique → rewrite cycles.",
        )
        quality_threshold = st.slider(
            "Quality threshold (1–5)",
            min_value=1, max_value=5,
            value=config.quality_threshold,
            step=1,
            key="uc3_threshold",
            help="All three scores (Clarity, Accuracy, Completeness) must reach this to pass.",
        )

    with st.expander("How does the reflection loop work?", expanded=False):
        st.markdown(
            "The agent cycles through three roles:\n\n"
            "1. **Generator** — writes an initial response (or a revision if a previous draft failed).\n"
            "2. **Critic** — scores the draft on Clarity, Accuracy, and Completeness (1–5 each).\n"
            "3. **Reviser** — if any score is below the threshold, the generator is called again "
            "with the critique embedded in the prompt.\n\n"
            "The loop stops when all scores ≥ threshold **or** when max revisions is reached."
        )
        st.table({
            "Score": ["1", "2", "3", "4", "5"],
            "Meaning": ["Very poor", "Below average", "Average", "Good", "Excellent"],
        })

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = ReflectionConfig(
            llm_model=model,
            temperature=temperature,
            max_revisions=max_revisions,
            quality_threshold=quality_threshold,
            system_prompt=setup.get("system_prompt", ReflectionConfig().system_prompt),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to execute the agent.")
