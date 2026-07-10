"""UC4 — Setup page: Research Team."""

import streamlit as st

from applications.mas_projects.uc4.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_SYSTEM_PROMPT = (
    "You are a research director overseeing a team of expert agents. "
    "Ensure the final report is comprehensive, accurate, and well-structured."
)

_CREW = [
    {
        "name": "📋 Planner",
        "role": "Breaks the query into specific research questions that together fully answer it.",
        "receives": "Original query",
    },
    {
        "name": "🔎 Researcher",
        "role": "Answers each research question using the Wikipedia API. Called once per question.",
        "receives": "One research question",
    },
    {
        "name": "📊 Analyst",
        "role": "Synthesises all research findings into key themes, connections, and implications.",
        "receives": "All findings",
    },
    {
        "name": "📝 Writer",
        "role": "Produces the final comprehensive report based on the analyst's synthesis.",
        "receives": "Full analysis",
    },
]

_SAMPLE_QUERIES = [
    "How does climate change affect global food security?",
    "What are the key factors behind the rise of large language models?",
    "How does the human immune system fight viral infections?",
    "What caused the 2008 financial crisis and what were the long-term effects?",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})

    st.markdown("#### Research crew")
    st.caption("Four specialist agents — memory accumulates across every stage.")

    cols = st.columns(len(_CREW))
    for col, member in zip(cols, _CREW):
        with col:
            with st.container(border=True):
                st.markdown(f"**{member['name']}**")
                st.caption(member["role"])
                st.caption(f"Input: `{member['receives']}`")

    st.markdown("#### Writer system prompt")
    st.caption("Customise how the Writer frames the final report.")
    system_prompt = st.text_area(
        "System prompt",
        value=setup.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        height=100,
        label_visibility="collapsed",
        key="mas_uc4_system_prompt",
    )

    if st.button("💾 Save Setup", use_container_width=False):
        st.session_state[AGENT_SETUP_SESSION_KEY] = {"system_prompt": system_prompt}
        st.success("Setup saved. Head to **Configure** to tune model parameters.")

    st.divider()
    st.markdown("#### Sample research queries")
    for q in _SAMPLE_QUERIES:
        st.caption(f"• {q}")
