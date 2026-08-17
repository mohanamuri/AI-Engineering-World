"""UC4 — Configure page."""

import streamlit as st
from applications.shared.groq_models import get_available_chat_models

from applications.agent_projects.services.multi_agent import MultiAgentConfig
from applications.agent_projects.uc4.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
)



def render() -> None:
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()
    _MODELS = st.session_state["_groq_models_cache"]

    st.subheader("⚙️ Configure")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: MultiAgentConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, MultiAgentConfig())

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model (all agents use the same model)",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="uc4_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="uc4_temperature",
        )
    with col2:
        max_rounds = st.slider(
            "Max supervisor rounds",
            min_value=2, max_value=10,
            value=config.max_rounds,
            step=1,
            key="uc4_max_rounds",
            help="Maximum number of supervisor → specialist → supervisor cycles.",
        )

    with st.expander("How does the Supervisor pattern work?", expanded=False):
        st.markdown(
            "The **Supervisor** is an LLM that reads the task and the accumulated work "
            "from all specialists, then decides who to call next:\n\n"
            "- `researcher` → Wikipedia lookup\n"
            "- `analyst` → Calculator\n"
            "- `writer` → Final synthesis\n"
            "- `FINISH` → Done\n\n"
            "After each specialist acts, control returns to the supervisor, which "
            "decides whether more work is needed. This continues until the supervisor "
            "routes to `writer` (who also forces a FINISH) or until max rounds is reached."
        )
        st.table({
            "Parameter": ["LLM model", "Temperature", "Max rounds"],
            "Effect": [
                "Same model used for all 4 agents (supervisor + 3 specialists)",
                "Low = consistent routing · High = creative variation",
                "Upper bound on total supervisor decisions",
            ],
        })

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = MultiAgentConfig(
            llm_model=model,
            temperature=temperature,
            max_rounds=max_rounds,
            system_prompt=setup.get("system_prompt", MultiAgentConfig().system_prompt),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to execute the agent team.")
