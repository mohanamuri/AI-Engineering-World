"""UC4 — Configure page: Research Team."""

import streamlit as st

from applications.mas_projects.services.research_team import ResearchTeamConfig
from applications.mas_projects.uc4.constants import (
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

    config: ResearchTeamConfig = st.session_state.get(
        AGENT_CONFIG_SESSION_KEY, ResearchTeamConfig()
    )

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "LLM model (all agents use the same model)",
            _MODELS,
            index=_MODELS.index(config.llm_model) if config.llm_model in _MODELS else 0,
            key="mas_uc4_model",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=config.temperature,
            step=0.05,
            key="mas_uc4_temperature",
        )
    with col2:
        max_questions = st.slider(
            "Research questions",
            min_value=1, max_value=4,
            value=config.max_questions,
            step=1,
            key="mas_uc4_max_questions",
            help="Number of sub-questions the Planner generates. Researcher is called once per question.",
        )

    with st.expander("How does the Research Team pattern work?", expanded=False):
        st.markdown(
            "This is the most complex MAS pattern on the platform. "
            "The key architectural feature is the **iterative research loop**: "
            "the Researcher node is called once per question in a cycle, "
            "accumulating findings before passing everything to the Analyst.\n\n"
            "The `route_researcher` conditional edge checks whether all questions "
            "have been answered:\n\n"
            "- More questions remain → back to Researcher\n"
            "- All questions answered → to Analyst\n\n"
            "| Parameter | Effect |\n"
            "|---|---|\n"
            "| LLM model | llama-3.3-70b recommended for research quality |\n"
            "| Temperature | 0 = consistent · Higher = creative synthesis |\n"
            "| Research questions | More = deeper coverage, longer runtime |"
        )

    if st.button("💾 Save Configuration", use_container_width=False):
        new_config = ResearchTeamConfig(
            llm_model=model,
            temperature=temperature,
            max_questions=max_questions,
            system_prompt=setup.get("system_prompt", ResearchTeamConfig().system_prompt),
        )
        st.session_state[AGENT_CONFIG_SESSION_KEY] = new_config
        st.success("Configuration saved. Head to **Run** to deploy the research team.")
