"""UC1 — Setup page: Supervisor Pipeline."""

import streamlit as st

from applications.mas_projects.uc1.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_SYSTEM_PROMPT = (
    "You are a senior analyst coordinating a research pipeline. "
    "Your team collects facts, processes them, and writes clear reports. "
    "Ensure the final summary is accurate, concise, and actionable."
)

_STAGES = [
    {
        "name": "🗂️ Collector",
        "role": "Researches the topic using the Wikipedia API to gather raw factual information.",
        "feeds_to": "Processor",
    },
    {
        "name": "🔬 Processor",
        "role": "Receives the Collector's output and extracts key facts, numbers, and themes.",
        "feeds_to": "Writer",
    },
    {
        "name": "✍️ Writer",
        "role": "Receives the Processor's analysis and writes a clear, structured prose response.",
        "feeds_to": "Supervisor",
    },
    {
        "name": "🧭 Supervisor",
        "role": "Receives the Writer's full response and produces a concise executive summary.",
        "feeds_to": "END",
    },
]

_SAMPLE_TASKS = [
    "What is machine learning and what industries does it impact most?",
    "Explain how solar panels work and their current efficiency rates.",
    "What is the history of the internet and how has it changed communication?",
    "Describe how vaccines work and their impact on public health.",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})

    st.markdown("#### Pipeline stages")
    st.caption("Four fixed stages — each agent receives the previous agent's output as input.")

    cols = st.columns(len(_STAGES))
    for col, stage in zip(cols, _STAGES):
        with col:
            with st.container(border=True):
                st.markdown(f"**{stage['name']}**")
                st.caption(stage["role"])
                st.caption(f"Feeds to: `{stage['feeds_to']}`")

    st.markdown("#### Supervisor system prompt")
    st.caption("Customise how the Supervisor frames its executive summary.")
    system_prompt = st.text_area(
        "System prompt",
        value=setup.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        height=100,
        label_visibility="collapsed",
        key="mas_uc1_system_prompt",
    )

    if st.button("💾 Save Setup", use_container_width=False):
        st.session_state[AGENT_SETUP_SESSION_KEY] = {"system_prompt": system_prompt}
        st.success("Setup saved. Head to **Configure** to tune model parameters.")

    st.divider()
    st.markdown("#### Sample tasks to try")
    for q in _SAMPLE_TASKS:
        st.caption(f"• {q}")
