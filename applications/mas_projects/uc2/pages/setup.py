"""UC2 — Setup page: Parallel Agents."""

import streamlit as st

from applications.mas_projects.uc2.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert synthesiser combining multiple independent expert "
    "perspectives into one comprehensive, balanced, and insightful response."
)

_AGENTS = [
    {
        "name": "📊 Facts Agent",
        "role": "Gathers encyclopaedic facts using the Wikipedia API. Focused on accuracy.",
        "independent": True,
    },
    {
        "name": "🔍 Critic Agent",
        "role": "Challenges assumptions, identifies risks, and surfaces counterarguments.",
        "independent": True,
    },
    {
        "name": "💡 Creative Agent",
        "role": "Offers novel angles, unexpected analogies, and broader implications.",
        "independent": True,
    },
    {
        "name": "🔀 Aggregator",
        "role": "Reads all three independent outputs and synthesises a comprehensive answer.",
        "independent": False,
    },
]

_SAMPLE_TASKS = [
    "Should AI be used in hiring decisions?",
    "What is the impact of social media on mental health?",
    "Is nuclear energy a viable solution to climate change?",
    "How has remote work changed the future of cities?",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})

    st.markdown("#### Agent team")
    st.caption("Three independent specialists run on the same task — no shared intermediate state.")

    cols = st.columns(len(_AGENTS))
    for col, agent in zip(cols, _AGENTS):
        with col:
            with st.container(border=True):
                st.markdown(f"**{agent['name']}**")
                st.caption(agent["role"])
                st.caption("Independent" if agent["independent"] else "Aggregates all outputs")

    st.markdown("#### Aggregator system prompt")
    st.caption("Customise how the Aggregator synthesises the three perspectives.")
    system_prompt = st.text_area(
        "System prompt",
        value=setup.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        height=100,
        label_visibility="collapsed",
        key="mas_uc2_system_prompt",
    )

    if st.button("💾 Save Setup", use_container_width=False):
        st.session_state[AGENT_SETUP_SESSION_KEY] = {"system_prompt": system_prompt}
        st.success("Setup saved. Head to **Configure** to tune model parameters.")

    st.divider()
    st.markdown("#### Sample tasks to try")
    for q in _SAMPLE_TASKS:
        st.caption(f"• {q}")
