"""UC3 — Export page: Image Intelligence."""

import json

import streamlit as st

from applications.media_projects.uc3.constants import (
    ANALYSIS_SESSION_KEY,
    QA_HISTORY_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)


def render() -> None:
    st.subheader("📥 Export")

    analysis = st.session_state.get(ANALYSIS_SESSION_KEY)
    if not analysis:
        st.warning("Process your image first.")
        return

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY, {})
    qa_history: list[dict] = st.session_state.get(QA_HISTORY_SESSION_KEY, [])
    stem = upload_data.get("filename", "image").rsplit(".", 1)[0]

    st.success("Image analysis ready to download.")

    report_dict = {
        "source_file": upload_data.get("filename", ""),
        "timestamp": analysis.timestamp,
        "description": analysis.description,
        "extracted_text": analysis.extracted_text,
        "objects": analysis.objects,
        "colours": analysis.colours,
        "qa_history": qa_history,
    }

    col1, col2 = st.columns(2)
    col1.download_button(
        label="⬇️ Analysis (JSON)",
        data=json.dumps(report_dict, indent=2, ensure_ascii=False),
        file_name=f"{stem}_analysis.json",
        mime="application/json",
        use_container_width=True,
    )
    col2.download_button(
        label="⬇️ Analysis (TXT)",
        data=_to_plain(analysis, qa_history, upload_data.get("filename", "")),
        file_name=f"{stem}_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.divider()
    st.markdown("#### Preview")
    tab1, tab2 = st.tabs(["Analysis", "Q&A History"])
    with tab1:
        st.markdown(f"**Description:** {analysis.description}")
        st.markdown(f"**Extracted text:** {analysis.extracted_text}")
        if analysis.objects:
            st.markdown(f"**Objects:** {' · '.join(analysis.objects)}")
        if analysis.colours:
            st.markdown(f"**Colours:** {' · '.join(analysis.colours)}")
    with tab2:
        if qa_history:
            for turn in qa_history:
                st.markdown(f"**Q:** {turn['q']}")
                st.markdown(f"**A:** {turn['a']}")
                st.divider()
        else:
            st.caption("No questions asked yet.")


def _to_plain(analysis, qa_history: list[dict], source: str) -> str:
    lines = [
        "Image Intelligence Report",
        f"Source: {source}",
        f"Generated: {analysis.timestamp[:19].replace('T', ' ')} UTC",
        "",
        "DESCRIPTION", "-----------", analysis.description,
        "", "EXTRACTED TEXT", "--------------", analysis.extracted_text,
        "", "OBJECTS DETECTED", "----------------",
        *[f"• {o}" for o in analysis.objects],
        "", "DOMINANT COLOURS", "----------------",
        *[f"• {c}" for c in analysis.colours],
    ]
    if qa_history:
        lines += ["", "Q&A HISTORY", "-----------"]
        for turn in qa_history:
            lines += [f"Q: {turn['q']}", f"A: {turn['a']}", ""]
    return "\n".join(lines)
