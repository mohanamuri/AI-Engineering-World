"""Throughput & scaling simulator for LLM APIs."""
from __future__ import annotations
from dataclasses import dataclass, field
import math


@dataclass
class ThroughputConfig:
    replicas: int = 1
    avg_latency_ms: float = 1600.0      # one request end-to-end
    cache_hit_rate: float = 0.0         # 0-1 (0 = no cache)
    batch_size: int = 1                 # requests batched per LLM call
    cache_latency_ms: float = 5.0       # time to serve a cache hit
    batch_overhead_ms: float = 50.0     # extra latency from batching


@dataclass
class ThroughputResult:
    config: ThroughputConfig
    rps_no_optimisation: float
    rps_with_cache: float
    rps_with_batching: float
    rps_with_both: float
    cache_throughput_gain_pct: float
    batch_throughput_gain_pct: float
    combined_gain_pct: float


def simulate_throughput(config: ThroughputConfig) -> ThroughputResult:
    """Compute RPS estimates for different optimisation combinations."""
    # Baseline: no cache, no batching
    base_rps = (config.replicas * 1000) / config.avg_latency_ms

    # With cache only: cache hits are served instantly, misses take full latency
    effective_latency_cache = (
        config.cache_hit_rate * config.cache_latency_ms +
        (1 - config.cache_hit_rate) * config.avg_latency_ms
    )
    rps_cache = (
        (config.replicas * 1000) / effective_latency_cache
        if effective_latency_cache > 0
        else base_rps
    )

    # With batching only: amortize LLM latency across batch_size requests
    # Effective latency per request = (latency + overhead) / batch_size
    effective_latency_batch = (config.avg_latency_ms + config.batch_overhead_ms) / config.batch_size
    rps_batch = (config.replicas * 1000) / effective_latency_batch

    # Both combined
    effective_combined = (
        config.cache_hit_rate * config.cache_latency_ms +
        (1 - config.cache_hit_rate) * effective_latency_batch
    )
    rps_both = (
        (config.replicas * 1000) / effective_combined
        if effective_combined > 0
        else rps_batch
    )

    cache_gain = (rps_cache - base_rps) / base_rps * 100 if base_rps > 0 else 0
    batch_gain = (rps_batch - base_rps) / base_rps * 100 if base_rps > 0 else 0
    combined_gain = (rps_both - base_rps) / base_rps * 100 if base_rps > 0 else 0

    return ThroughputResult(
        config=config,
        rps_no_optimisation=base_rps,
        rps_with_cache=rps_cache,
        rps_with_batching=rps_batch,
        rps_with_both=rps_both,
        cache_throughput_gain_pct=cache_gain,
        batch_throughput_gain_pct=batch_gain,
        combined_gain_pct=combined_gain,
    )


def simulate_scaling_curve(max_replicas: int, base_config: ThroughputConfig) -> list[dict]:
    """Generate RPS vs replicas data for a scaling chart."""
    results = []
    for r in range(1, max_replicas + 1):
        cfg = ThroughputConfig(
            replicas=r,
            avg_latency_ms=base_config.avg_latency_ms,
            cache_hit_rate=base_config.cache_hit_rate,
            batch_size=base_config.batch_size,
            cache_latency_ms=base_config.cache_latency_ms,
            batch_overhead_ms=base_config.batch_overhead_ms,
        )
        res = simulate_throughput(cfg)
        results.append({
            "replicas": r,
            "rps_baseline": res.rps_no_optimisation,
            "rps_cache": res.rps_with_cache,
            "rps_batching": res.rps_with_batching,
            "rps_both": res.rps_with_both,
        })
    return results
