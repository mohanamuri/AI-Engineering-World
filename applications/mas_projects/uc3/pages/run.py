"""UC3 — Run page: Debate & Judge."""

import streamlit as st

from applications.mas_projects.services.debate_judge import (
    DebateConfig,
    DebateRound,
    DebateRun,
    run_debate,
)
from applications.mas_projects.uc3.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_TOPICS = [
    "AI will replace most white-collar jobs within 20 years.",
    "Social media does more harm than good to society.",
    "Remote work is better for productivity than office work.",
    "Universal Basic Income should be implemented globally.",
]

_WINNER_LABELS = {
    "proponent": "🟦 Proponent wins",
    "opponent":  "🟥 Opponent wins",
    "draw":      "🤝 Draw",
}


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: DebateConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, DebateConfig())
    history: list[DebateRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample debate topic:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_TOPICS):
            if cols[i % 2].button(q, key=f"mas_uc3_sample_{i}", use_container_width=True):
                _run_debate(q, config)
                st.rerun()
        st.divider()

    for run in history:
        with st.chat_message("user"):
            st.write(f"**Topic:** {run.topic}")
        with st.chat_message("assistant"):
            winner_label = _WINNER_LABELS.get(run.winner, "Unknown")
            st.markdown(f"**Verdict: {winner_label}**")
            st.caption(run.judgment)
            with st.expander("Full debate transcript", expanded=False):
                _render_debate(run.rounds)

    topic = st.chat_input("Enter a debate topic or proposition…")
    if topic:
        _run_debate(topic, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear debate history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_debate(rounds: list[DebateRound]) -> None:
    for entry in rounds:
        if entry.agent == "proponent":
            st.markdown(f"**🟦 Proponent — Round {entry.round_num}**")
        else:
            st.markdown(f"**🟥 Opponent — Round {entry.round_num}**")
        st.write(entry.argument)
        st.divider()


def _run_debate(topic: str, config: DebateConfig) -> None:
    with st.spinner(f"Debate in progress ({config.num_rounds} round(s))…"):
        try:
            result = run_debate(topic, config)
        except Exception as exc:
            st.error(f"Debate failed: {exc}")
            return
    history: list[DebateRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
