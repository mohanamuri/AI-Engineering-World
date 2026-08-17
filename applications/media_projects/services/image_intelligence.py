"""
Image Intelligence — Media UC3.

Pipeline:
  Upload image (.jpg/.png)
  → Groq Vision (compound-beta-mini)
  → Describe scene, extract embedded text, detect objects
  → Interactive Q&A about the image
"""

from __future__ import annotations

import base64
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


def _build_image_message(prompt: str, image_bytes: bytes, filename: str) -> HumanMessage:
    ext = os.path.splitext(filename)[-1].lower()
    mime = _MIME_MAP.get(ext, "image/jpeg")
    b64 = _encode_image(image_bytes)
    return HumanMessage(content=[
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        {"type": "text", "text": prompt},
    ])


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ImageConfig:
    vision_model: str = "compound-beta-mini"
    temperature: float = 0.2


@dataclass
class ImageAnalysis:
    description: str
    extracted_text: str
    objects: list[str]
    colours: list[str]
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

_ANALYSE_PROMPT = """\
Analyse this image and return ONLY valid JSON (no markdown, no extra text):
{
  "description": "A detailed 3-5 sentence description of what is in the image",
  "extracted_text": "All visible text found in the image, or 'No text found'",
  "objects": ["object1", "object2", "object3"],
  "colours": ["dominant colour 1", "dominant colour 2"]
}"""


def analyse_image(image_bytes: bytes, filename: str, config: ImageConfig) -> ImageAnalysis:
    """Run full image analysis: description, text extraction, objects, colours."""
    import json

    llm = ChatGroq(
        model=config.vision_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    msg = _build_image_message(_ANALYSE_PROMPT, image_bytes, filename)
    resp = llm.invoke([
        SystemMessage(content="You are a precise vision AI. Return only valid JSON."),
        msg,
    ])
    raw = resp.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)
    return ImageAnalysis(
        description=data.get("description", ""),
        extracted_text=data.get("extracted_text", ""),
        objects=data.get("objects", []),
        colours=data.get("colours", []),
    )


def ask_about_image(
    question: str,
    image_bytes: bytes,
    filename: str,
    config: ImageConfig,
    context: str = "",
) -> str:
    """Answer a user question about an image."""
    llm = ChatGroq(
        model=config.vision_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    system = "You are a helpful vision assistant. Answer questions about the provided image clearly and concisely."
    if context:
        system += f"\n\nInitial analysis context:\n{context}"

    msg = _build_image_message(question, image_bytes, filename)
    resp = llm.invoke([SystemMessage(content=system), msg])
    return resp.content.strip()
