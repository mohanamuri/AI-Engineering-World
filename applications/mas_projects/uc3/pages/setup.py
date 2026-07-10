"""UC3 — Setup page: Debate & Judge."""

import streamlit as st

from applications.mas_projects.uc3.constants import AGENT_SETUP_SESSION_KEY

_DEFAULT_PROPONENT = "You are arguing strongly in FAVOUR of the proposition."
_DEFAULT_OPPONENT = "You are arguing strongly AGAINST the proposition."

_SAMPLE_TOPICS = [
    "AI will replace most white-collar jobs within 20 years.",
    "Social media does more harm than good to society.",
    "Remote work is better for productivity than office work.",
    "Universal Basic Income should be implemented globally.",
]


def render() -> None:
    st.subheader("🛠️ Setup")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY, {})

    st.markdown("#### Debate format")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("**🟦 Proponent**")
            st.caption("Argues FOR the proposition. Persuasive and specific.")
    with col2:
        with st.container(border=True):
            st.markdown("**🟥 Opponent**")
            st.caption("Argues AGAINST the proposition. Equally persuasive.")
    with col3:
        with st.container(border=True):
            st.markdown("**⚖️ Judge**")
            st.caption("Evaluates both sides on logic, evidence, and persuasion.")

    st.markdown("#### Agent personas")
    col_a, col_b = st.columns(2)
    with col_a:
        proponent_persona = st.text_area(
            "Proponent persona",
            value=setup.get("proponent_persona", _DEFAULT_PROPONENT),
            height=80,
            key="mas_uc3_proponent_persona",
        )
    with col_b:
        opponent_persona = st.text_area(
            "Opponent persona",
            value=setup.get("opponent_persona", _DEFAULT_OPPONENT),
            height=80,
            key="mas_uc3_opponent_persona",
        )

    if st.button("💾 Save Setup", use_container_width=False):
        st.session_state[AGENT_SETUP_SESSION_KEY] = {
            "proponent_persona": proponent_persona,
            "opponent_persona": opponent_persona,
        }
        st.success("Setup saved. Head to **Configure** to set number of rounds.")

    st.divider()
    st.markdown("#### Sample debate topics")
    for q in _SAMPLE_TOPICS:
        st.caption(f"• {q}")
