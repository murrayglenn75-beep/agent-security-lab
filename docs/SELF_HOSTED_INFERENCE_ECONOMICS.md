# Self-hosted inference economics and release-readiness evidence

Source: user-supplied October 2026 LinkedIn screenshots of a single reported Modal 4×H200/vLLM GLM-5.3-Flash coding-agent session. All figures are **third-party self-reported**, not validated here. Session: 1,534 requests, 110.7M input tokens, 0.99M output tokens, 94% reported prefix-cache hits, roughly $62 GPU charge. No equivalent task-quality comparison was reported. Do not treat the reported dollar figures as current cloud prices.

## Patterns to reuse

- Gate readiness on *successful bounded generation*, not only an HTTP health endpoint. Failure or timeout means not ready.
- Preflight estimated or measured input tokens **plus** requested output against a verified context limit and provider output bound. Reject unsupported context configurations.
- Record cold-start versus warmed latencies separately; model-loading and compiler caches must be verified per runtime rather than assumed.
- Benchmark concurrency, time to first token, sustained throughput, cache behavior, failed task rate and cost per **successful** representative task. Report idle accelerator costs.
- Compare equivalent evaluated tasks and privacy requirements, not only nominal token rates.
- Use controlled workload shape and report the measurement provenance. The included Python functions validate caller-supplied data; they do **not** measure GPU/LLM inference.

## Adoption candidates

APEX: CPU-first evaluation with RAM, latency, task quality, context and swap measurements—four H200 GPUs are not a target deployment. FORGE: readiness and distributed worker capacity gate plus sustained workload tests. TANDEM: user-facing model capability selection and cost/latency reporting. AAK: approve provider use and high-impact effects independently, with quota reservation where applicable. Agent Security Lab: reusable pure-function assurance tests.

## Known limitations

The capacity checks require trusted token counts: character lengths are not token counts. Model context is not the same as total request budget. Caller-provided benchmarks have no independent provenance. Pricing, billing, provider caching, and quality must be validated in actual deployments. No model deployment, live load test, persistent cache, cost telemetry, or automatic routing changes are implemented by this PR.
