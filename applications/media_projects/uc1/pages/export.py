"""UC1 — Export page: Meeting Intelligence."""

import json

import streamlit as st

from applications.media_projects.uc1.constants import (
    ANALYSIS_SESSION_KEY,
    TRANSCRIPT_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)


def render() -> None:
    st.subheader("📥 Export")

    report = st.session_state.get(ANALYSIS_SESSION_KEY)
    if not report:
        st.warning("Complete **Analyse** first.")
        return

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY, {})
    transcript_result = st.session_state.get(TRANSCRIPT_SESSION_KEY)
    stem = upload_data.get("filename", "meeting").rsplit(".", 1)[0]

    st.success("Your meeting report is ready.")

    col1, col2, col3 = st.columns(3)

    report_dict = {
        "source_file": upload_data.get("filename", ""),
        "timestamp": report.timestamp,
        "summary": report.summary,
        "decisions": report.decisions,
        "action_items": report.action_items,
        "sentiment": report.sentiment,
        "key_topics": report.key_topics,
        "transcript": report.transcript,
    }
    col1.download_button(
        label="⬇️ Report (JSON)",
        data=json.dumps(report_dict, indent=2, ensure_ascii=False),
        file_name=f"{stem}_report.json",
        mime="application/json",
        use_container_width=True,
    )

    col2.download_button(
        label="⬇️ Report (TXT)",
        data=_to_plain(report, upload_data.get("filename", "")),
        file_name=f"{stem}_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

    if transcript_result:
        col3.download_button(
            label="⬇️ Transcript",
            data=transcript_result.text,
            file_name=f"{stem}_transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.divider()
    st.markdown("#### Preview")
    tab1, tab2 = st.tabs(["Report", "Transcript"])
    with tab1:
        st.markdown(f"**Summary:** {report.summary}")
        st.markdown(f"**Sentiment:** {report.sentiment}")
        if report.decisions:
            st.markdown("**Decisions:**")
            for d in report.decisions:
                st.markdown(f"- {d}")
        if report.action_items:
            st.markdown("**Action Items:**")
            for a in report.action_items:
                st.markdown(f"- {a}")
        if report.key_topics:
            st.markdown(f"**Key Topics:** {' · '.join(report.key_topics)}")
    with tab2:
        if transcript_result:
            st.text(transcript_result.text[:3000] + ("…" if len(transcript_result.text) > 3000 else ""))
        else:
            st.caption("No transcript available.")


def _to_plain(report, source: str) -> str:
    lines = [
        "Meeting Intelligence Report",
        f"Source: {source}",
        f"Generated: {report.timestamp[:19].replace('T', ' ')} UTC",
        "",
        "SUMMARY", "-------", report.summary, "",
        "DECISIONS", "---------",
        *[f"• {d}" for d in report.decisions],
        "", "ACTION ITEMS", "------------",
        *[f"• {a}" for a in report.action_items],
        "", "SENTIMENT", "---------", report.sentiment,
        "", "KEY TOPICS", "----------",
        *[f"• {t}" for t in report.key_topics],
        "", "TRANSCRIPT", "----------", report.transcript,
    ]
    return "\n".join(lines)
