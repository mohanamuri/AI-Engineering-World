"""UC2 — Analyse page: Video Intelligence (same LLM extraction as UC1)."""

import streamlit as st

from applications.media_projects.services.video_intelligence import VideoConfig, analyse_video
from applications.media_projects.uc2.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    TRANSCRIPT_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)


def render() -> None:
    st.subheader("🧠 Analyse")

    transcript_result = st.session_state.get(TRANSCRIPT_SESSION_KEY)
    if not transcript_result:
        st.warning("Extract and transcribe the video first (← Extract tab).")
        return

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY, {})
    config: VideoConfig = st.session_state.get(CONFIG_SESSION_KEY, VideoConfig())
    report = st.session_state.get(ANALYSIS_SESSION_KEY)

    if report is None:
        st.info(
            f"Using **{config.llm_model}** — same extraction pipeline as Meeting Intelligence: "
            "summary · decisions · action items · sentiment · key topics."
        )
        if st.button("🧠 Analyse Video", type="primary", use_container_width=False):
            with st.spinner("Extracting insights from transcript…"):
                try:
                    result = analyse_video(
                        transcript_result.text,
                        upload_data.get("filename", "video"),
                        config,
                    )
                    st.session_state[ANALYSIS_SESSION_KEY] = result
                    st.rerun()
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
    else:
        st.success("Analysis complete. Head to **Export** →")

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
