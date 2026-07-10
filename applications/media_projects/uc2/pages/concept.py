"""Media UC2 — Concept page: Video Intelligence."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Video Intelligence — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why video files need an extra step before speech-to-text\n"
        "- What ffmpeg does and why it's needed\n"
        "- How the UC1 pipeline (Whisper + LLM) works the same way on video\n"
        "- What 'audio extraction' means in plain English"
    )

    # ── Build on UC1 ─────────────────────────────────────────────────────────
    st.markdown("### Building on UC1 — One Extra Step")

    st.markdown(
        "UC1 (Meeting Intelligence) already handles audio files perfectly. "
        "But what if you have a **video recording** — a Zoom call, a screen recording, "
        "or a camera recording of a presentation?\n\n"
        "Video files contain two things: **picture data** (what you see) and **audio data** (what you hear). "
        "Whisper only needs the audio — it can't process the video frames.\n\n"
        "**UC2 adds one step before the UC1 pipeline: extract the audio from the video file.**"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1 — Audio file input**")
            st.markdown(
                "Input: .mp3 / .wav / .m4a\n\n"
                "→ Whisper transcribes\n"
                "→ LLM extracts report\n"
                "→ Done"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC2 — Video file input**")
            st.markdown(
                "Input: .mp4 / .mov / .avi\n\n"
                "→ **ffmpeg extracts audio** ← new step\n"
                "→ Whisper transcribes (same as UC1)\n"
                "→ LLM extracts report (same as UC1)\n"
                "→ Done"
            )

    # ── Visual ───────────────────────────────────────────────────────────────
    st.markdown("### How It Works — Video → Audio → Text → Report")

    st.graphviz_chart("""
    digraph VideoIntelligence {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        V  [label="🎬 Video File\n(.mp4 / .mov)" fillcolor="#fce7f3" color="#ec4899"]
        F  [label="ffmpeg\nExtract audio track\n(16kHz mono MP3)" fillcolor="#e0e7ff" color="#6366f1"]
        W  [label="Groq Whisper\nSpeech → Text\n(transcript)" fillcolor="#dbeafe" color="#3b82f6"]
        L  [label="Groq LLM\nStructured\nextraction" fillcolor="#fef9c3" color="#eab308"]
        R  [label="📋 Meeting Report" fillcolor="#f0fdf4" color="#22c55e"]

        V -> F -> W -> L -> R
        F -> F [label="strips video\nkeeps audio" style=dashed]
    }
    """)

    steps = [
        ("🎬 Step 1 — Upload your video",
         "Upload any .mp4, .mov, or .avi file — a recorded Zoom call, Teams meeting, "
         "presentation recording, or camera video."),
        ("🔊 Step 2 — ffmpeg extracts the audio",
         "**ffmpeg** is a free, open-source tool that can process video and audio files. "
         "Here it's used to strip out just the audio track from your video "
         "and save it as a compressed MP3 at 16 kHz (the optimal format for Whisper). "
         "This step takes a few seconds. The video frames are discarded — "
         "only the sound matters."),
        ("🎙️ Step 3 → 📋 Step 4 — Same as UC1",
         "From here, the pipeline is identical to Meeting Intelligence:\n"
         "- Whisper converts the extracted audio to text\n"
         "- The LLM reads the transcript and extracts a structured report\n\n"
         "You get the same quality output whether you started with audio or video."),
    ]
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    # ── Key terms ────────────────────────────────────────────────────────────
    st.markdown("### Key Terms (Plain English)")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**ffmpeg**")
            st.write(
                "A free, open-source command-line tool for processing audio and video files. "
                "It can convert formats, extract audio tracks, compress, trim, and much more. "
                "Here it does one thing: pull the audio out of a video file."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Audio Extraction / Demuxing**")
            st.write(
                "A video file 'muxes' (combines) video and audio into one file. "
                "'Demuxing' separates them. "
                "Extracting the audio track means saving just the sound — no picture data."
            )

    st.success(
        "**Ready to try it?** Go to **Upload** and load a video file. "
        "ffmpeg will extract the audio automatically — you won't need to do anything manually. "
        "Then proceed through Transcribe → Analyse → Export."
    )
