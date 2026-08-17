"""UC1 — Configure page: Supervisor Pipeline."""

import streamlit as st

from applications.mas_projects.services.supervisor_pipeline import SupervisorPipelineConfig
from applications.mas_projects.uc1.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
)

_MODELS = [
    "qwen/qwen3-32b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
]


def render() -> None:
    st.subheader("⚙️ Configure")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: SupervisorPipelineConfig = st.session_state.get(
        AGENT_CONFIG_SESSION_KEY, SupervisorPipelineConfig()
    )

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model (all stages use the same model)",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="mas_uc1_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="mas_uc1_temperature",
        )
    with col2:
        st.info(
            "The Supervisor Pipeline runs 4 fixed stages sequentially. "
            "No routing decisions — the flow is always Collector → Processor → Writer → Supervisor."
        )

    with st.expander("How does the Pipeline pattern work?", expanded=False):
        st.markdown(
            "Unlike a dynamic supervisor that decides who acts next, this pipeline "
            "is **deterministic**: each stage always runs in the same order.\n\n"
            "The key architectural feature is **chained context**: each agent "
            "receives the previous agent's full output as its primary input. "
            "Knowledge accumulates from stage to stage, so the Writer has richer "
            "material than the Collector ever saw.\n\n"
            "| Parameter | Effect |\n"
            "|---|---|\n"
            "| LLM model | Same model used across all 4 stages |\n"
            "| Temperature | Low = consistent · High = creative variation |"
        )

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = SupervisorPipelineConfig(
            llm_model=model,
            temperature=temperature,
            system_prompt=setup.get("system_prompt", SupervisorPipelineConfig().system_prompt),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to execute the pipeline.")
