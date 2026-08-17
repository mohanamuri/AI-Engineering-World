"""
Meeting Intelligence — Media UC1.

Pipeline:
  Upload audio (.mp3/.wav/.m4a)
  → Groq Whisper transcription
  → LLM extracts: summary, decisions, action items, sentiment, key topics
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MeetingConfig:
    whisper_model: str = "whisper-large-v3"
    llm_model: str = "compound-beta-mini"
    temperature: float = 0.0


@dataclass
class TranscriptResult:
    text: str
    duration: float = 0.0


@dataclass
class MeetingReport:
    transcript: str
    summary: str
    decisions: list[str]
    action_items: list[str]
    sentiment: str
    key_topics: list[str]
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------------

_MIME_MAP = {
    ".mp3":  "audio/mpeg",
    ".wav":  "audio/wav",
    ".m4a":  "audio/mp4",
    ".ogg":  "audio/ogg",
    ".flac": "audio/flac",
}


def transcribe_audio(audio_bytes: bytes, filename: str, config: MeetingConfig) -> TranscriptResult:
    """Transcribe audio using Groq Whisper."""
    from groq import Groq
    ext = os.path.splitext(filename)[-1].lower()
    mime = _MIME_MAP.get(ext, "audio/mpeg")

    client = Groq(api_key=_get_groq_api_key())
    transcription = client.audio.transcriptions.create(
        file=(filename, audio_bytes, mime),
        model=config.whisper_model,
        response_format="verbose_json",
    )
    duration = getattr(transcription, "duration", 0.0) or 0.0
    return TranscriptResult(text=transcription.text, duration=float(duration))


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

_ANALYSIS_PROMPT = """\
You are an expert meeting analyst. Analyse the transcript below and return a structured report.

Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{{
  "summary": "2-3 sentence executive summary of the meeting",
  "decisions": ["decision 1", "decision 2"],
  "action_items": ["Owner: action description", "Owner: action description"],
  "sentiment": "Positive | Neutral | Mixed | Negative — with a brief reason",
  "key_topics": ["topic 1", "topic 2", "topic 3"]
}}

Transcript:
{transcript}
"""


def analyse_meeting(transcript: str, config: MeetingConfig) -> MeetingReport:
    """Extract structured insights from a transcript using an LLM."""
    import json

    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    resp = llm.invoke([
        SystemMessage(content="You are an expert meeting analyst. Return only valid JSON."),
        HumanMessage(content=_ANALYSIS_PROMPT.format(transcript=transcript[:8000])),
    ])
    raw = resp.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)
    return MeetingReport(
        transcript=transcript,
        summary=data.get("summary", ""),
        decisions=data.get("decisions", []),
        action_items=data.get("action_items", []),
        sentiment=data.get("sentiment", ""),
        key_topics=data.get("key_topics", []),
    )
