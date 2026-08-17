"""
Memory Patterns Service

Three memory strategies for multi-turn LLM conversations:
  Buffer Memory   — keep last N messages verbatim
  Summary Memory  — summarise old turns, keep summary + recent messages
  Entity Memory   — extract named entities, maintain a fact store across turns

All implemented with Groq. No LangChain memory required.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime

from groq import Groq

_MODEL = "qwen/qwen3-32b"
BUFFER_WINDOW = 6        # last N messages to keep in buffer memory
SUMMARY_TRIGGER = 6      # summarise when history exceeds this many messages


@dataclass
class Message:
    role: str    # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class MemoryState:
    memory_type: str               # "buffer" | "summary" | "entity"
    messages: list[Message]        # full turn history (for display)
    context_sent: list[dict]       # actual messages sent to LLM this turn
    summary: str = ""              # summary memory only
    entities: dict = field(default_factory=dict)  # entity memory only
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0


# ── Buffer Memory ─────────────────────────────────────────────────────────────

def chat_buffer(user_msg: str, history: list[Message], temperature: float = 0.7) -> MemoryState:
    """Keep only the last BUFFER_WINDOW messages as context."""
    recent = history[-BUFFER_WINDOW:] if len(history) > BUFFER_WINDOW else history
    context = [{"role": m.role, "content": m.content} for m in recent]
    context.append({"role": "user", "content": user_msg})

    client = Groq()
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=_MODEL, temperature=temperature, max_tokens=512,
        messages=[{"role": "system", "content": "You are a helpful assistant."}] + context,
    )
    lat = (time.perf_counter() - t0) * 1000
    output = resp.choices[0].message.content or ""
    ti = resp.usage.prompt_tokens if resp.usage else 0
    to = resp.usage.completion_tokens if resp.usage else 0

    new_history = history + [
        Message(role="user", content=user_msg),
        Message(role="assistant", content=output),
    ]
    return MemoryState(
        memory_type="buffer", messages=new_history, context_sent=context,
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


# ── Summary Memory ────────────────────────────────────────────────────────────

def _summarise(messages: list[Message]) -> str:
    conversation = "\n".join(f"{m.role.upper()}: {m.content}" for m in messages)
    client = Groq()
    resp = client.chat.completions.create(
        model=_MODEL, temperature=0.0, max_tokens=256,
        messages=[
            {"role": "system", "content": "Summarise this conversation in 3-5 bullet points, preserving key facts."},
            {"role": "user", "content": conversation},
        ],
    )
    return resp.choices[0].message.content or ""


def chat_summary(
    user_msg: str,
    history: list[Message],
    current_summary: str,
    temperature: float = 0.7,
) -> MemoryState:
    """Summarise old turns; keep summary + recent 4 messages."""
    recent_cutoff = 4
    if len(history) > SUMMARY_TRIGGER and len(history) % 2 == 0:
        to_summarise = history[:-recent_cutoff]
        current_summary = _summarise(to_summarise)
        history = history[-recent_cutoff:]

    context = []
    if current_summary:
        context.append({"role": "user", "content": f"[Conversation summary so far]\n{current_summary}"})
        context.append({"role": "assistant", "content": "Understood. I'll keep that context in mind."})
    for m in history:
        context.append({"role": m.role, "content": m.content})
    context.append({"role": "user", "content": user_msg})

    client = Groq()
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=_MODEL, temperature=temperature, max_tokens=512,
        messages=[{"role": "system", "content": "You are a helpful assistant."}] + context,
    )
    lat = (time.perf_counter() - t0) * 1000
    output = resp.choices[0].message.content or ""
    ti = resp.usage.prompt_tokens if resp.usage else 0
    to_tok = resp.usage.completion_tokens if resp.usage else 0

    new_history = history + [
        Message(role="user", content=user_msg),
        Message(role="assistant", content=output),
    ]
    return MemoryState(
        memory_type="summary", messages=new_history, context_sent=context,
        summary=current_summary, tokens_in=ti, tokens_out=to_tok, latency_ms=lat,
    )


# ── Entity Memory ─────────────────────────────────────────────────────────────

def _extract_entities(text: str) -> dict:
    client = Groq()
    resp = client.chat.completions.create(
        model=_MODEL, temperature=0.0, max_tokens=256,
        messages=[
            {"role": "system", "content": (
                "Extract named entities from the text. "
                "Return ONLY valid JSON: {\"person\": [], \"place\": [], \"org\": [], \"fact\": []}. "
                "No markdown, no explanation."
            )},
            {"role": "user", "content": text},
        ],
    )
    raw = resp.choices[0].message.content or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def chat_entity(
    user_msg: str,
    history: list[Message],
    entities: dict,
    temperature: float = 0.7,
) -> MemoryState:
    """Extract entities each turn; inject fact store into system prompt."""
    new_entities = _extract_entities(user_msg)
    for key, vals in new_entities.items():
        entities.setdefault(key, [])
        for v in vals:
            if v not in entities[key]:
                entities[key].append(v)

    entity_context = ""
    if any(entities.values()):
        lines = []
        for k, vs in entities.items():
            if vs:
                lines.append(f"{k.capitalize()}: {', '.join(vs)}")
        entity_context = "Known entities from this conversation:\n" + "\n".join(lines)

    system = "You are a helpful assistant." + (f"\n\n{entity_context}" if entity_context else "")
    context = [{"role": m.role, "content": m.content} for m in history]
    context.append({"role": "user", "content": user_msg})

    client = Groq()
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=_MODEL, temperature=temperature, max_tokens=512,
        messages=[{"role": "system", "content": system}] + context,
    )
    lat = (time.perf_counter() - t0) * 1000
    output = resp.choices[0].message.content or ""
    ti = resp.usage.prompt_tokens if resp.usage else 0
    to_tok = resp.usage.completion_tokens if resp.usage else 0

    new_history = history + [
        Message(role="user", content=user_msg),
        Message(role="assistant", content=output),
    ]
    return MemoryState(
        memory_type="entity", messages=new_history, context_sent=context,
        entities=entities, tokens_in=ti, tokens_out=to_tok, latency_ms=lat,
    )
