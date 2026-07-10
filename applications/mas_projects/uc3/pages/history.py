"""UC3 — History page: Debate & Judge."""

import streamlit as st

from applications.mas_projects.services.debate_judge import DebateRun
from applications.mas_projects.uc3.constants import RUN_HISTORY_SESSION_KEY

_WINNER_LABELS = {
    "proponent": "🟦 Proponent wins",
    "opponent":  "🟥 Opponent wins",
    "draw":      "🤝 Draw",
}


def render() -> None:
    st.subheader("📜 History")

    history: list[DebateRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No debates yet. Go to **Run** to start a debate.")
        return

    st.caption(f"{len(history)} debate(s) this session")

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        winner_label = _WINNER_LABELS.get(run.winner, "Unknown")
        label = f"Debate {n}: {run.topic[:60]}{'…' if len(run.topic) > 60 else ''} — {winner_label}"
        with st.expander(label, expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)
            col1.metric("Rounds", len([r for r in run.rounds if r.agent == "proponent"]))
            col2.metric("Winner", winner_label)
            col3.metric("Timestamp", run.timestamp[:19].replace("T", " "))

            st.markdown("**Judge's verdict**")
            st.write(run.judgment)

            st.markdown("**Debate transcript**")
            for entry in run.rounds:
                if entry.agent == "proponent":
                    st.markdown(f"🟦 **Proponent — Round {entry.round_num}**")
                else:
                    st.markdown(f"🟥 **Opponent — Round {entry.round_num}**")
                st.write(entry.argument)
                st.divider()
