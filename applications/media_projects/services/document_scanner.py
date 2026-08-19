"""
Document Scanner — Media UC4.

Pipeline:
  Upload photo of document / whiteboard / slide (.jpg/.png)
  → Groq Vision (openai/gpt-oss-20b)
  → Structured extraction: title, sections, content blocks, metadata
  → Export as JSON or plain text
"""

from __future__ import annotations

import base64
import json
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


_MIME_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".webp": "image/webp",
}


def _encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ScannerConfig:
    vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.0
    document_type: str = "auto"  # auto | meeting_notes | whiteboard | slide | form | report


@dataclass
class DocumentContent:
    document_type: str
    title: str
    sections: list[dict]   # [{"heading": str, "content": str}]
    all_text: str          # flat verbatim extraction
    metadata: dict         # language, has_tables, has_diagrams, word_count
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

_EXTRACTION_PROMPT = """\
You are a document digitisation AI. Extract all content from the document/whiteboard/slide in this image.

Return ONLY valid JSON in exactly this format (no markdown, no extra text):
{{
  "document_type": "meeting_notes | whiteboard | slide | form | report | other",
  "title": "document title or 'Untitled'",
  "sections": [
    {{"heading": "Section heading or empty string", "content": "Full text content of this section"}}
  ],
  "all_text": "Complete verbatim text extracted from the image",
  "metadata": {{
    "language": "detected language",
    "has_tables": true,
    "has_diagrams": false,
    "estimated_word_count": 0
  }}
}}

Be thorough — extract every word visible in the image."""


def scan_document(image_bytes: bytes, filename: str, config: ScannerConfig) -> DocumentContent:
    """Extract structured content from a document image using Groq Vision."""
    ext = os.path.splitext(filename)[-1].lower()
    mime = _MIME_MAP.get(ext, "image/jpeg")
    b64 = _encode_image(image_bytes)

    llm = ChatGroq(
        model=config.vision_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )

    prompt = _EXTRACTION_PROMPT
    if config.document_type != "auto":
        prompt += f"\n\nHint: This is a {config.document_type}."

    msg = HumanMessage(content=[
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        {"type": "text", "text": prompt},
    ])
    resp = llm.invoke([
        SystemMessage(content="You are a document digitisation AI. Return only valid JSON."),
        msg,
    ])
    raw = resp.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)

    return DocumentContent(
        document_type=data.get("document_type", "other"),
        title=data.get("title", "Untitled"),
        sections=data.get("sections", []),
        all_text=data.get("all_text", ""),
        metadata=data.get("metadata", {}),
    )


def to_plain_text(doc: DocumentContent) -> str:
    """Convert DocumentContent to a clean plain-text string for export."""
    lines = [
        f"Document Scanner — Extracted Content",
        f"Type: {doc.document_type}",
        f"Title: {doc.title}",
        f"Extracted: {doc.timestamp[:19].replace('T', ' ')} UTC",
        "",
    ]
    for sec in doc.sections:
        if sec.get("heading"):
            lines.append(f"## {sec['heading']}")
        lines.append(sec.get("content", ""))
        lines.append("")
    return "\n".join(lines)
