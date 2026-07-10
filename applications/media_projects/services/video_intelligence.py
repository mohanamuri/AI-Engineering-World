"""
Video Intelligence — Media UC2.

Pipeline:
  Upload video (.mp4/.mov)
  → ffmpeg extracts audio (16 kHz mono MP3)
  → Groq Whisper transcription
  → LLM extracts: summary, decisions, action items, sentiment, key topics
  (same structured report as UC1)
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone

from applications.media_projects.services.meeting_intelligence import (
    MeetingConfig,
    MeetingReport,
    TranscriptResult,
    analyse_meeting,
    transcribe_audio,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class VideoConfig(MeetingConfig):
    """Same config as MeetingConfig — video uses the same Whisper + LLM pipeline."""
    pass


@dataclass
class VideoReport(MeetingReport):
    """Identical to MeetingReport with an added source video filename."""
    video_filename: str = ""


# ---------------------------------------------------------------------------
# ffmpeg audio extraction
# ---------------------------------------------------------------------------

def extract_audio_from_video(video_bytes: bytes, video_ext: str) -> bytes:
    """Extract audio from video bytes using ffmpeg. Returns MP3 bytes."""
    with tempfile.NamedTemporaryFile(suffix=video_ext, delete=False) as tmp_vid:
        tmp_vid.write(video_bytes)
        tmp_vid_path = tmp_vid.name

    tmp_audio_path = tmp_vid_path.replace(video_ext, "_audio.mp3")
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", tmp_vid_path,
                "-vn",                   # drop video stream
                "-acodec", "libmp3lame",
                "-ar", "16000",          # 16 kHz — optimal for Whisper
                "-ac", "1",              # mono
                "-q:a", "4",
                tmp_audio_path,
                "-y",                    # overwrite without asking
            ],
            check=True,
            capture_output=True,
        )
        with open(tmp_audio_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(tmp_vid_path):
            os.unlink(tmp_vid_path)
        if os.path.exists(tmp_audio_path):
            os.unlink(tmp_audio_path)


# ---------------------------------------------------------------------------
# Public runners
# ---------------------------------------------------------------------------

def process_video(video_bytes: bytes, filename: str, config: VideoConfig) -> TranscriptResult:
    """Extract audio from video then transcribe with Groq Whisper."""
    ext = os.path.splitext(filename)[-1].lower()
    audio_bytes = extract_audio_from_video(video_bytes, ext)
    audio_filename = filename.rsplit(".", 1)[0] + ".mp3"
    return transcribe_audio(audio_bytes, audio_filename, config)


def analyse_video(transcript: str, video_filename: str, config: VideoConfig) -> VideoReport:
    """Analyse video transcript — same LLM extraction as Meeting Intelligence."""
    base = analyse_meeting(transcript, config)
    return VideoReport(
        transcript=base.transcript,
        summary=base.summary,
        decisions=base.decisions,
        action_items=base.action_items,
        sentiment=base.sentiment,
        key_topics=base.key_topics,
        video_filename=video_filename,
    )
