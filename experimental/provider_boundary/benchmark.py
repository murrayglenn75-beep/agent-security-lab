"""Offline deterministic benchmark of stub adapters (not real model latency)."""
import json
import statistics
import time

from provider_boundary import Provider, ProviderError, Request, Response, invoke


def run(samples=100):
    if not isinstance(samples, int) or not 1 <= samples <= 10000:
        raise ValueError("invalid sample count")
    def fail(_):
        raise ProviderError("FIXTURE_TEMPORARY", retryable=True)
    def succeed(r):
        return Response("ok", "secondary", r.model, 10, 5, 0.0)
    providers = [
        Provider("primary", fail, frozenset({"fixture"}), frozenset({"public"}), 64),
        Provider("secondary", succeed, frozenset({"fixture"}), frozenset({"public"}), 64),
    ]
    measurements = []
    for i in range(samples):
        req = Request(str(i), "synthetic prompt", "fixture", 32, 1000, 0.0,
                      allow_fallback=True)
        start = time.perf_counter_ns()
        response, attempts = invoke(req, providers,
                                    {"allowed_providers": {"primary", "secondary"}})
        measurements.append((time.perf_counter_ns() - start) / 1_000_000)
        assert response.text == "ok" and len(attempts) == 1
    return {"type": "synthetic_python_routing_overhead_only",
            "samples": samples,
            "median_ms": statistics.median(measurements),
            "p95_ms": sorted(measurements)[int(.95 * (samples - 1))],
            "fallback_success": samples,
            "external_api_requests": 0,
            "provider_cost_usd": 0.0}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
