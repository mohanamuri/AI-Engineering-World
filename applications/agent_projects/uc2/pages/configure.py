"""UC2 — Configure page."""

import streamlit as st

from applications.agent_projects.services.plan_execute_agent import PlanExecuteConfig
from applications.agent_projects.uc2.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
)

_MODELS = [
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
    "qwen/qwen3-32b",
]


def render() -> None:
    st.subheader("⚙️ Configure")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: PlanExecuteConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, PlanExecuteConfig())

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="uc2_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="uc2_temperature",
        )
    with col2:
        max_plan_steps = st.slider(
            "Max plan steps",
            min_value=2, max_value=8,
            value=config.max_plan_steps,
            step=1,
            key="uc2_max_steps",
            help="Upper bound on how many steps the planner can create.",
        )
        st.markdown("##### Active tools")
        for t in setup.get("enabled_tools", []):
            st.caption(f"✓ {t}")

    with st.expander("How does Plan-and-Execute differ from ReAct?", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**ReAct (UC1)**")
            st.caption("Decides what to do one step at a time. No upfront plan.")
        with col_b:
            st.markdown("**Plan-and-Execute (UC2)**")
            st.caption("Creates a complete plan first, then executes each step in order.")
        st.table({
            "Parameter": ["LLM model", "Temperature", "Max plan steps"],
            "Effect": [
                "Larger model = better planning quality",
                "Low = consistent plans · High = creative variation",
                "More steps = finer-grained execution (but more LLM calls)",
            ],
        })

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = PlanExecuteConfig(
            llm_model=model,
            temperature=temperature,
            max_plan_steps=max_plan_steps,
            enabled_tools=setup.get("enabled_tools", ["calculator", "wikipedia"]),
            system_prompt=setup.get("system_prompt", PlanExecuteConfig().system_prompt),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to execute the agent.")
