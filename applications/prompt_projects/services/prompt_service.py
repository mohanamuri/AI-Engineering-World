"""
Prompt Engineering Services

Implements four prompting patterns, all powered by Groq free tier:
  UC1 — Zero-shot vs Few-shot
  UC2 — Chain-of-Thought (CoT)
  UC3 — Structured Output (JSON schema)
  UC4 — Prompt Chaining (Outline → Draft → Refine)
"""

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime

from groq import Groq

_DEFAULT_MODEL = "compound-beta-mini"


@dataclass
class PromptConfig:
    model: str = _DEFAULT_MODEL
    temperature: float = 0.7
    max_tokens: int = 1024


@dataclass
class PromptResult:
    output: str
    prompt_used: str
    technique: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class ChainStep:
    label: str
    prompt: str
    output: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0


@dataclass
class ChainResult:
    steps: list[ChainStep]
    final_output: str
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


def _call(system: str, user: str, config: PromptConfig) -> tuple[str, int, int, float]:
    """Call Groq and return (output, tokens_in, tokens_out, latency_ms)."""
    client = Groq()
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    latency_ms = (time.perf_counter() - t0) * 1000
    output = response.choices[0].message.content or ""
    tokens_in = response.usage.prompt_tokens if response.usage else 0
    tokens_out = response.usage.completion_tokens if response.usage else 0
    return output, tokens_in, tokens_out, latency_ms


# ── UC1: Zero-shot vs Few-shot ────────────────────────────────────────────────

def run_zero_shot(task: str, config: PromptConfig) -> PromptResult:
    """No examples — raw instruction only."""
    system = "You are a helpful assistant. Complete the task the user gives you."
    output, ti, to, lat = _call(system, task, config)
    return PromptResult(
        output=output, prompt_used=task, technique="Zero-shot",
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


def run_few_shot(task: str, examples: list[dict], config: PromptConfig) -> PromptResult:
    """examples: [{'input': str, 'output': str}]"""
    system = "You are a helpful assistant. Study the examples carefully, then complete the task in the same style."
    example_block = "\n\n".join(
        f"Example {i + 1}:\nInput: {ex['input']}\nOutput: {ex['output']}"
        for i, ex in enumerate(examples)
    )
    prompt = f"{example_block}\n\nNow complete this:\nInput: {task}\nOutput:"
    output, ti, to, lat = _call(system, prompt, config)
    return PromptResult(
        output=output, prompt_used=prompt, technique="Few-shot",
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


# ── UC2: Chain-of-Thought ─────────────────────────────────────────────────────

def run_direct(question: str, config: PromptConfig) -> PromptResult:
    """Direct answer — no reasoning trace."""
    system = "You are a helpful assistant. Answer questions clearly and concisely."
    output, ti, to, lat = _call(system, question, config)
    return PromptResult(
        output=output, prompt_used=question, technique="Direct",
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


def run_cot(question: str, config: PromptConfig) -> PromptResult:
    """Chain-of-Thought — explicit step-by-step reasoning."""
    system = "You are a careful reasoner. Always think through problems step by step before giving a final answer."
    prompt = f"{question}\n\nLet's think through this step by step:"
    output, ti, to, lat = _call(system, prompt, config)
    return PromptResult(
        output=output, prompt_used=prompt, technique="Chain-of-Thought",
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


# ── UC3: Structured Output ────────────────────────────────────────────────────

DEFAULT_SCHEMA = {
    "title": "string — main topic or title",
    "summary": "string — 2-3 sentence overview",
    "key_points": ["string — point 1", "string — point 2", "string — point 3"],
    "sentiment": "positive | neutral | negative",
    "confidence": "high | medium | low",
}


def run_freeform(task: str, config: PromptConfig) -> PromptResult:
    """Unstructured freeform response."""
    system = "You are a helpful assistant."
    output, ti, to, lat = _call(system, task, config)
    return PromptResult(
        output=output, prompt_used=task, technique="Freeform",
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


def run_structured(task: str, schema: dict, config: PromptConfig) -> PromptResult:
    """Force JSON output matching the given schema."""
    schema_str = json.dumps(schema, indent=2)
    system = (
        "You are a structured data extractor. "
        "Output ONLY valid JSON — no markdown fences, no preamble, no explanation."
    )
    prompt = (
        f"Task: {task}\n\n"
        f"Return ONLY a valid JSON object that matches this schema exactly:\n{schema_str}"
    )
    output, ti, to, lat = _call(system, prompt, config)
    # Strip markdown fences if the model wraps output
    output = re.sub(r"```(?:json)?\s*|\s*```", "", output).strip()
    return PromptResult(
        output=output, prompt_used=prompt, technique="Structured Output",
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


# ── UC4: Prompt Chaining ──────────────────────────────────────────────────────

def run_single_prompt(task: str, config: PromptConfig) -> PromptResult:
    """Single monolithic prompt — baseline for comparison."""
    system = "You are a skilled writer and analyst. Complete the task thoroughly and well."
    output, ti, to, lat = _call(system, task, config)
    return PromptResult(
        output=output, prompt_used=task, technique="Single Prompt",
        tokens_in=ti, tokens_out=to, latency_ms=lat,
    )


def run_chain(task: str, config: PromptConfig) -> ChainResult:
    """Three-step chain: Outline → Draft → Refine."""
    steps: list[ChainStep] = []
    total_ti = total_to = 0
    total_lat = 0.0

    # Step 1 — Outline
    sys1 = "You are a strategic planner. Create only a concise numbered outline — no prose."
    p1 = f"Create a clear numbered outline for this task:\n\n{task}"
    o1, ti1, to1, lat1 = _call(sys1, p1, config)
    steps.append(ChainStep(label="1 — Outline", prompt=p1, output=o1,
                            tokens_in=ti1, tokens_out=to1, latency_ms=lat1))
    total_ti += ti1; total_to += to1; total_lat += lat1

    # Step 2 — Draft
    sys2 = "You are a skilled writer. Expand each outline point into detailed, well-written content."
    p2 = f"Original task: {task}\n\nOutline:\n{o1}\n\nExpand each point into full content:"
    o2, ti2, to2, lat2 = _call(sys2, p2, config)
    steps.append(ChainStep(label="2 — Draft", prompt=p2, output=o2,
                            tokens_in=ti2, tokens_out=to2, latency_ms=lat2))
    total_ti += ti2; total_to += to2; total_lat += lat2

    # Step 3 — Refine
    sys3 = "You are an editor. Polish the draft for clarity, flow, and impact. Remove any redundancy."
    p3 = f"Polish and refine this draft:\n\n{o2}"
    o3, ti3, to3, lat3 = _call(sys3, p3, config)
    steps.append(ChainStep(label="3 — Refine", prompt=p3, output=o3,
                            tokens_in=ti3, tokens_out=to3, latency_ms=lat3))
    total_ti += ti3; total_to += to3; total_lat += lat3

    return ChainResult(
        steps=steps,
        final_output=o3,
        total_tokens_in=total_ti,
        total_tokens_out=total_to,
        total_latency_ms=total_lat,
    )
