"""Media UC1 — Concept page: Meeting Intelligence."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Meeting Intelligence — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- How AI converts speech (audio) to text automatically\n"
        "- How an LLM reads a transcript and extracts a structured report\n"
        "- What 'structured extraction' means and why it's useful\n"
        "- How to go from one audio file to a complete meeting report"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — Manual Meeting Notes Are Painful")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Without Meeting Intelligence**")
            st.markdown(
                "- Someone has to take notes manually during the meeting\n"
                "- Notes are incomplete — people miss things while listening\n"
                "- Action items get lost or forgotten\n"
                "- No searchable record of what was decided\n"
                "- Review takes as long as the meeting itself"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**With Meeting Intelligence**")
            st.markdown(
                "- Upload the recording — done in seconds\n"
                "- Full word-for-word transcript automatically\n"
                "- Summary, decisions, action items extracted automatically\n"
                "- Sentiment analysis of the overall meeting tone\n"
                "- Structured report ready for sharing or filing"
            )

    # ── Two-stage pipeline ────────────────────────────────────────────────────
    st.markdown("### How It Works — Two Stages")

    st.graphviz_chart("""
    digraph MeetingIntelligence {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        A  [label="🎙️ Audio File\n(.mp3 / .wav / .m4a)" fillcolor="#fce7f3" color="#ec4899"]
        W  [label="Groq Whisper\nSpeech → Text\n(transcript)" fillcolor="#dbeafe" color="#3b82f6"]
        L  [label="Groq LLM\nReads transcript\nextracts structure" fillcolor="#fef9c3" color="#eab308"]
        R  [label="📋 Meeting Report\nSummary · Decisions\nActions · Sentiment" fillcolor="#f0fdf4" color="#22c55e"]

        A -> W -> L -> R
    }
    """)

    stages = [
        ("🎙️ Stage 1 — Speech to Text (Whisper)",
         "You upload an audio file. **Groq Whisper** — a state-of-the-art speech recognition model — "
         "converts the spoken words into a text transcript automatically.\n\n"
         "Whisper handles:\n"
         "- Multiple speakers\n"
         "- Background noise\n"
         "- Different accents\n"
         "- Technical vocabulary\n\n"
         "The result is a full, accurate transcript of everything said in the meeting."),
        ("🧠 Stage 2 — Structured Extraction (LLM)",
         "The LLM reads the full transcript and extracts specific information in a structured format:\n\n"
         "- **Summary** — 3–5 sentences covering the key discussion points\n"
         "- **Decisions made** — what was agreed, approved, or rejected\n"
         "- **Action items** — who needs to do what, by when\n"
         "- **Sentiment** — was the overall tone positive, neutral, or tense?\n"
         "- **Key topics** — main themes discussed\n\n"
         "This is called **structured extraction**: the LLM doesn't just summarise freely — "
         "it fills in a specific template every time, making the output consistent and machine-readable."),
    ]
    for title, body in stages:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    # ── Key terms ────────────────────────────────────────────────────────────
    st.markdown("### Key Terms (Plain English)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("**Whisper**")
            st.write(
                "An AI model built specifically for converting speech to text. "
                "It was created by OpenAI and runs here via Groq's fast inference API. "
                "No internet streaming required — the audio is processed as a file."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Structured Extraction**")
            st.write(
                "Instead of free-form summarisation, the LLM fills in a fixed template: "
                "summary here, decisions here, action items here. "
                "Every report has the same structure — easy to read, compare, and file."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Sentiment Analysis**")
            st.write(
                "The LLM reads the tone of the conversation — not just the words — "
                "and classifies it: positive (productive, enthusiastic), "
                "neutral (factual, calm), or negative (tense, frustrated)."
            )

    st.success(
        "**Ready to try it?** Go to **Upload** and load an audio recording. "
        "Then **Transcribe** to get the full text, and **Analyse** to get the complete report. "
        "Export as JSON or plain text when done."
    )
