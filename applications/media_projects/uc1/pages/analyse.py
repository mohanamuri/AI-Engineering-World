"""UC1 — Analyse page: Meeting Intelligence (LLM structured extraction)."""

import streamlit as st

from applications.media_projects.services.meeting_intelligence import (
    MeetingConfig,
    analyse_meeting,
)
from applications.media_projects.uc1.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    TRANSCRIPT_SESSION_KEY,
)


def render() -> None:
    st.subheader("🧠 Analyse")

    transcript_result = st.session_state.get(TRANSCRIPT_SESSION_KEY)
    if not transcript_result:
        st.warning("Transcribe your audio first (← Transcribe tab).")
        return

    config: MeetingConfig = st.session_state.get(CONFIG_SESSION_KEY, MeetingConfig())
    report = st.session_state.get(ANALYSIS_SESSION_KEY)

    if report is None:
        st.info(
            f"Using **{config.llm_model}** to extract: "
            "summary · decisions · action items · sentiment · key topics."
        )
        if st.button("🧠 Analyse Meeting", type="primary", use_container_width=False):
            with st.spinner("Extracting meeting insights…"):
                try:
                    result = analyse_meeting(transcript_result.text, config)
                    st.session_state[ANALYSIS_SESSION_KEY] = result
                    st.rerun()
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
    else:
        st.success("Analysis complete. Head to **Export** to download your report →")

        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("#### Summary")
            st.write(report.summary)

            st.markdown("#### Decisions")
            if report.decisions:
                for d in report.decisions:
                    st.markdown(f"- {d}")
            else:
                st.caption("No decisions extracted.")

            st.markdown("#### Action Items")
            if report.action_items:
                for a in report.action_items:
                    st.markdown(f"- {a}")
            else:
                st.caption("No action items extracted.")

        with col2:
            st.markdown("#### Sentiment")
            st.info(report.sentiment or "—")

            st.markdown("#### Key Topics")
            for t in report.key_topics:
                st.markdown(f"- {t}")

        if st.button("🔄 Re-analyse"):
            st.session_state.pop(ANALYSIS_SESSION_KEY, None)
            st.rerun()
