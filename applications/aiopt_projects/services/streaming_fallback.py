"""
Streaming + Fallback Service

Streaming  — return tokens as they generate (perceived latency drops dramatically)
Fallback   — if primary model fails or rate-limits, retry then switch to backup model

Both patterns are essential in production LLM systems.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generator

from groq import Groq

PRIMARY_MODEL  = "llama-3.1-8b-instant"
FALLBACK_MODEL = "llama-3.1-70b-versatile"
MAX_RETRIES    = 2


@dataclass
class StreamResult:
    model_used: str
    tokens_out: int = 0
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class FallbackResult:
    output: str
    model_used: str
    attempts: int
    fell_back: bool
    error_message: str = ""
    latency_ms: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


def stream_response(prompt: str, model: str = PRIMARY_MODEL, temperature: float = 0.7) -> Generator[str, None, None]:
    """Yield tokens as they stream from Groq."""
    client = Groq()
    stream = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=1024,
        stream=True,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def run_blocking(prompt: str, model: str = PRIMARY_MODEL, temperature: float = 0.7) -> FallbackResult:
    """Non-streaming call — wait for full response."""
    client = Groq()
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    lat = (time.perf_counter() - t0) * 1000
    output = resp.choices[0].message.content or ""
    ti = resp.usage.prompt_tokens if resp.usage else 0
    to = resp.usage.completion_tokens if resp.usage else 0
    return FallbackResult(
        output=output, model_used=model, attempts=1,
        fell_back=False, latency_ms=lat, tokens_in=ti, tokens_out=to,
    )


def run_with_fallback(
    prompt: str,
    primary: str = PRIMARY_MODEL,
    fallback: str = FALLBACK_MODEL,
    temperature: float = 0.7,
    force_fallback: bool = False,
) -> FallbackResult:
    """
    Try primary model up to MAX_RETRIES times.
    If all attempts fail, switch to fallback model.
    force_fallback=True simulates a primary failure for demo purposes.
    """
    client = Groq()
    attempts = 0
    last_error = ""

    if not force_fallback:
        for attempt in range(1, MAX_RETRIES + 1):
            attempts = attempt
            try:
                t0 = time.perf_counter()
                resp = client.chat.completions.create(
                    model=primary,
                    temperature=temperature,
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                )
                lat = (time.perf_counter() - t0) * 1000
                output = resp.choices[0].message.content or ""
                ti = resp.usage.prompt_tokens if resp.usage else 0
                to = resp.usage.completion_tokens if resp.usage else 0
                return FallbackResult(
                    output=output, model_used=primary, attempts=attempts,
                    fell_back=False, latency_ms=lat, tokens_in=ti, tokens_out=to,
                )
            except Exception as exc:
                last_error = str(exc)
                time.sleep(0.5 * attempt)

    # Fallback
    attempts += 1
    try:
        t0 = time.perf_counter()
        resp = client.chat.completions.create(
            model=fallback,
            temperature=temperature,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        lat = (time.perf_counter() - t0) * 1000
        output = resp.choices[0].message.content or ""
        ti = resp.usage.prompt_tokens if resp.usage else 0
        to = resp.usage.completion_tokens if resp.usage else 0
        return FallbackResult(
            output=output, model_used=fallback, attempts=attempts,
            fell_back=True, error_message=last_error,
            latency_ms=lat, tokens_in=ti, tokens_out=to,
        )
    except Exception as exc:
        return FallbackResult(
            output="Both primary and fallback models failed.",
            model_used=fallback, attempts=attempts,
            fell_back=True, error_message=str(exc), latency_ms=0.0,
        )
