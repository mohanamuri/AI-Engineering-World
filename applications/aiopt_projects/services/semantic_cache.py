"""
Semantic Cache Service

Instead of exact-match caching, embeds queries and finds semantically
similar cached responses. A cache hit avoids an LLM call entirely.

Pattern used in production to reduce API costs and latency.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer

_EMBED_MODEL: SentenceTransformer | None = None
_DEFAULT_LLM = "llama-3.1-8b-instant"
DEFAULT_THRESHOLD = 0.85


@dataclass
class CacheEntry:
    query: str
    response: str
    embedding: list[float]
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class CacheResult:
    output: str
    cache_hit: bool
    similarity: float        # 0.0 on miss
    latency_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    model_used: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


def load_embed_model() -> SentenceTransformer:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL


def embed(text: str) -> list[float]:
    model = load_embed_model()
    return model.encode(text).tolist()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(np.dot(va, vb) / denom) if denom > 0 else 0.0


def find_in_cache(
    query_embedding: list[float],
    cache: list[CacheEntry],
    threshold: float,
) -> tuple[CacheEntry, float] | None:
    """Return (best_entry, similarity) if above threshold, else None."""
    best_entry, best_sim = None, 0.0
    for entry in cache:
        sim = _cosine_similarity(query_embedding, entry.embedding)
        if sim > best_sim:
            best_sim, best_entry = sim, entry
    if best_entry and best_sim >= threshold:
        return best_entry, best_sim
    return None


def run_with_cache(
    question: str,
    cache: list[CacheEntry],
    threshold: float = DEFAULT_THRESHOLD,
    model: str = _DEFAULT_LLM,
    temperature: float = 0.3,
) -> tuple[CacheResult, list[CacheEntry]]:
    """
    Query with semantic cache.
    Returns (result, updated_cache).
    """
    t0 = time.perf_counter()
    q_emb = embed(question)
    embed_ms = (time.perf_counter() - t0) * 1000

    hit = find_in_cache(q_emb, cache, threshold)
    if hit:
        entry, sim = hit
        return CacheResult(
            output=entry.response,
            cache_hit=True,
            similarity=sim,
            latency_ms=embed_ms,
            model_used="cache",
        ), cache

    # Cache miss — call LLM
    client = Groq()
    t1 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=512,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer concisely."},
            {"role": "user", "content": question},
        ],
    )
    llm_ms = (time.perf_counter() - t1) * 1000
    output = response.choices[0].message.content or ""
    ti = response.usage.prompt_tokens if response.usage else 0
    to = response.usage.completion_tokens if response.usage else 0

    new_cache = cache + [CacheEntry(query=question, response=output, embedding=q_emb)]
    return CacheResult(
        output=output,
        cache_hit=False,
        similarity=0.0,
        latency_ms=embed_ms + llm_ms,
        tokens_in=ti,
        tokens_out=to,
        model_used=model,
    ), new_cache
