"""
Model Routing Service

A lightweight classifier reads the query and decides which model to use:
  - Simple queries  → meta-llama/llama-4-scout-17b-16e-instruct  (fast, low cost)
  - Complex queries → meta-llama/llama-4-maverick-17b-128e-instruct (slower, higher quality)

Pattern used in production to control cost without sacrificing quality.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime

from groq import Groq

SMALL_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
LARGE_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"

_ROUTER_PROMPT = """You are a query complexity classifier.

Classify the query as SIMPLE or COMPLEX based on these rules:
- SIMPLE: factual lookup, single-step calculation, yes/no question,
  basic definition, short creative task, common knowledge.
- COMPLEX: multi-step reasoning, deep analysis, code generation,
  research synthesis, nuanced judgment, long-form content.

Respond with ONLY one word: SIMPLE or COMPLEX."""


@dataclass
class RoutingDecision:
    complexity: str          # "SIMPLE" or "COMPLEX"
    model_selected: str
    routing_reason: str
    routing_latency_ms: float


@dataclass
class RouterResult:
    output: str
    routing: RoutingDecision
    tokens_in: int = 0
    tokens_out: int = 0
    llm_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


def classify_query(query: str) -> tuple[str, float]:
    """Return (SIMPLE|COMPLEX, latency_ms)."""
    client = Groq()
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=SMALL_MODEL,
        temperature=0.0,
        max_tokens=5,
        messages=[
            {"role": "system", "content": _ROUTER_PROMPT},
            {"role": "user", "content": f"Query: {query}"},
        ],
    )
    lat = (time.perf_counter() - t0) * 1000
    label = resp.choices[0].message.content.strip().upper()
    if "COMPLEX" in label:
        return "COMPLEX", lat
    return "SIMPLE", lat


def run_routed(query: str, temperature: float = 0.7) -> RouterResult:
    """Classify → select model → run query."""
    complexity, routing_ms = classify_query(query)

    if complexity == "COMPLEX":
        model = LARGE_MODEL
        reason = "Multi-step reasoning or deep analysis detected → routed to 70B model."
    else:
        model = SMALL_MODEL
        reason = "Simple factual or single-step task → routed to 8B model for speed."

    routing = RoutingDecision(
        complexity=complexity,
        model_selected=model,
        routing_reason=reason,
        routing_latency_ms=routing_ms,
    )

    client = Groq()
    t1 = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
    )
    llm_ms = (time.perf_counter() - t1) * 1000
    output = resp.choices[0].message.content or ""
    ti = resp.usage.prompt_tokens if resp.usage else 0
    to = resp.usage.completion_tokens if resp.usage else 0

    return RouterResult(
        output=output,
        routing=routing,
        tokens_in=ti,
        tokens_out=to,
        llm_latency_ms=llm_ms,
        total_latency_ms=routing_ms + llm_ms,
    )


def run_fixed_model(query: str, model: str, temperature: float = 0.7) -> RouterResult:
    """Run on a specific model without routing — for comparison."""
    routing = RoutingDecision(
        complexity="N/A",
        model_selected=model,
        routing_reason="Fixed model — no routing.",
        routing_latency_ms=0.0,
    )
    client = Groq()
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
    )
    lat = (time.perf_counter() - t0) * 1000
    output = resp.choices[0].message.content or ""
    ti = resp.usage.prompt_tokens if resp.usage else 0
    to = resp.usage.completion_tokens if resp.usage else 0
    return RouterResult(
        output=output, routing=routing,
        tokens_in=ti, tokens_out=to,
        llm_latency_ms=lat, total_latency_ms=lat,
    )
