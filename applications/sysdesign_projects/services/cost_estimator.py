"""Monthly cost estimator for LLM + RAG systems."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CostConfig:
    # Traffic
    monthly_requests: int = 10_000
    avg_input_tokens: int = 1000         # prompt tokens per request
    avg_output_tokens: int = 500         # completion tokens per request
    cache_hit_rate: float = 0.30         # fraction served from cache

    # Model pricing (per 1M tokens)
    input_token_cost_per_1m: float = 0.10    # USD
    output_token_cost_per_1m: float = 0.15   # USD

    # Embedding
    monthly_doc_updates: int = 100        # new docs/month to embed
    avg_doc_tokens: int = 2000
    embedding_cost_per_1m: float = 0.02   # HuggingFace = free; OpenAI = $0.02

    # Infrastructure
    vector_db_monthly_usd: float = 0.0    # 0 = ChromaDB local
    cache_monthly_usd: float = 0.0        # 0 = in-memory
    hosting_monthly_usd: float = 7.0      # Render free tier = $0, paid = $7+


@dataclass
class CostBreakdown:
    llm_input_usd: float
    llm_output_usd: float
    embedding_usd: float
    vector_db_usd: float
    cache_usd: float
    hosting_usd: float
    total_usd: float
    cost_per_request_cents: float
    savings_from_cache_usd: float
    cache_roi_pct: float    # savings / cache_cost * 100


def estimate_monthly_cost(config: CostConfig) -> CostBreakdown:
    # LLM calls (only for cache misses)
    llm_requests = config.monthly_requests * (1 - config.cache_hit_rate)
    input_tokens_m = (llm_requests * config.avg_input_tokens) / 1_000_000
    output_tokens_m = (llm_requests * config.avg_output_tokens) / 1_000_000

    llm_input = input_tokens_m * config.input_token_cost_per_1m
    llm_output = output_tokens_m * config.output_token_cost_per_1m

    # Embedding cost
    embed_tokens_m = (config.monthly_doc_updates * config.avg_doc_tokens) / 1_000_000
    embedding = embed_tokens_m * config.embedding_cost_per_1m

    total = (
        llm_input + llm_output + embedding +
        config.vector_db_monthly_usd + config.cache_monthly_usd + config.hosting_monthly_usd
    )
    cost_per_req_cents = (total / config.monthly_requests * 100) if config.monthly_requests > 0 else 0

    # Cache savings: requests that would have hit LLM but didn't
    cached_requests = config.monthly_requests * config.cache_hit_rate
    savings_input = (cached_requests * config.avg_input_tokens / 1_000_000) * config.input_token_cost_per_1m
    savings_output = (cached_requests * config.avg_output_tokens / 1_000_000) * config.output_token_cost_per_1m
    savings = savings_input + savings_output

    cache_cost = config.cache_monthly_usd
    roi = (savings / cache_cost * 100) if cache_cost > 0 else float("inf")

    return CostBreakdown(
        llm_input_usd=llm_input,
        llm_output_usd=llm_output,
        embedding_usd=embedding,
        vector_db_usd=config.vector_db_monthly_usd,
        cache_usd=config.cache_monthly_usd,
        hosting_usd=config.hosting_monthly_usd,
        total_usd=total,
        cost_per_request_cents=cost_per_req_cents,
        savings_from_cache_usd=savings,
        cache_roi_pct=roi,
    )


MODEL_PRICING = {
    "Groq Free Tier (openai/gpt-oss-20b)": {"input": 0.0, "output": 0.0},
    "OpenAI GPT-4o mini": {"input": 0.15, "output": 0.60},
    "OpenAI GPT-4o": {"input": 2.50, "output": 10.00},
    "Anthropic Claude Haiku": {"input": 0.25, "output": 1.25},
    "Anthropic Claude Sonnet": {"input": 3.00, "output": 15.00},
    "AWS Bedrock Llama 3 8B": {"input": 0.22, "output": 0.22},
}
