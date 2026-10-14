"""Deterministic preflight and benchmark report validation; no provider calls."""
from dataclasses import dataclass
from math import isfinite
from statistics import median


@dataclass(frozen=True)
class Capacity:
    context_tokens: int
    max_output_tokens: int
    allows_prefix_cache: bool = False


def preflight(input_tokens, requested_output_tokens, capacity):
    if not isinstance(capacity, Capacity):
        raise ValueError("missing capacity")
    for value in (input_tokens, requested_output_tokens, capacity.context_tokens,
                  capacity.max_output_tokens):
        if type(value) is not int or value < 1:
            raise ValueError("invalid token bound")
    if requested_output_tokens > capacity.max_output_tokens:
        raise ValueError("output exceeds provider limit")
    if input_tokens + requested_output_tokens > capacity.context_tokens:
        raise ValueError("request exceeds context capacity")
    return True


def readiness(generate_probe, expected="READY"):
    """True only when a real generation probe returns the expected text.

    Caller must supply a trusted, bounded, inference-only probe; do not use for
    privileged effects. The API deliberately has no health-endpoint fallback.
    """
    try:
        return generate_probe() == expected
    except Exception:
        return False


def benchmark_report(samples, *, cold_start_seconds=None, idle_cost_usd=0.0,
                     total_cost_usd=0.0, successful_tasks=0,
                     attempts=None, cache_hits=None):
    if not samples or any(type(x) not in (int, float) or
                          not isfinite(x) or x < 0 for x in samples):
        raise ValueError("invalid latency samples")
    if type(successful_tasks) is not int or successful_tasks < 0:
        raise ValueError("invalid success count")
    if any(type(x) not in (int, float) or not isfinite(x) or x < 0
           for x in (idle_cost_usd, total_cost_usd)):
        raise ValueError("invalid cost")
    if idle_cost_usd > total_cost_usd:
        raise ValueError("idle cost cannot exceed total")
    if cold_start_seconds is not None and (type(cold_start_seconds) not in (int, float)
                                           or not isfinite(cold_start_seconds)
                                           or cold_start_seconds < 0):
        raise ValueError("invalid cold start")
    if attempts is not None and (type(attempts) is not int or
                                 attempts < len(samples) or successful_tasks > attempts):
        raise ValueError("invalid attempt count")
    if cache_hits is not None and (type(cache_hits) is not int or
                                    cache_hits < 0 or attempts is None or
                                    cache_hits > attempts):
        raise ValueError("invalid cache count")
    ordered = sorted(samples)
    return {
        "evidence_type": "caller_supplied_measurements_not_independently_verified",
        "sample_count": len(samples),
        "median_ms": median(ordered),
        "p95_ms": ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)],
        "cold_start_seconds": cold_start_seconds,
        "idle_cost_usd": idle_cost_usd,
        "total_cost_usd": total_cost_usd,
        "successful_tasks": successful_tasks,
        "cost_per_successful_task_usd": (
            total_cost_usd / successful_tasks if successful_tasks else None),
        "failure_count": (attempts - successful_tasks) if attempts is not None else None,
        "cache_hit_fraction": (cache_hits / attempts if attempts else None)
        if cache_hits is not None else None,
    }
