"""UC3 — History page."""

import streamlit as st

from applications.agent_projects.services.reflection_agent import ReflectionRun
from applications.agent_projects.uc3.constants import RUN_HISTORY_SESSION_KEY


def _score_color(score: int, threshold: int) -> str:
    if score >= threshold:
        return "🟢"
    if score >= threshold - 1:
        return "🟡"
    return "🔴"


def render() -> None:
    st.subheader("📜 History")

    history: list[ReflectionRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No runs yet. Go to **Run** to execute the agent.")
        return

    st.caption(f"{len(history)} run(s) this session")

    # Use a default threshold for display since config may not be in scope here
    threshold = 4

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        label = f"Run {n}: {run.task[:70]}{'…' if len(run.task) > 70 else ''}"
        with st.expander(label, expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)
            col1.metric("Drafts", len(run.drafts))
            last = run.drafts[-1] if run.drafts else None
            col2.metric("Final avg score", f"{last.avg}/5" if last else "—")
            passed_drafts = sum(1 for d in run.drafts if d.scores_ok(threshold))
            col3.metric("Drafts passed", passed_drafts)

            st.markdown("**Final answer**")
            st.write(run.final_answer)

            st.markdown("**Draft scorecard**")
            for dr in run.drafts:
                passed = dr.scores_ok(threshold)
                status = "✅ Passed" if passed else "❌ Failed"
                st.markdown(
                    f"Draft {dr.draft_number} — {status}  ·  "
                    f"Clarity:{dr.clarity} Accuracy:{dr.accuracy} Completeness:{dr.completeness}  ·  "
                    f"avg {dr.avg}/5"
                )

            st.caption(f"Timestamp: {run.timestamp}")
