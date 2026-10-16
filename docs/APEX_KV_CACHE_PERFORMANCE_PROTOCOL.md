# APEX KV-cache and inference memory evaluation — planned, not measured

The experimental Python estimator calculates the idealized raw K/V tensor allocation:
layers × KV heads × head dimension × cached tokens × simultaneous sequences ×
(key element bytes + value element bytes). It excludes padding, block allocator fragmentation,
model weights, activations, OS processes, runtime overhead and potential non-standard attention layouts.
Quantization metadata and implementation-specific allocation must be measured. It is NOT an
APEX or llama.cpp integration and DOES NOT demonstrate speed, accuracy or lower memory.

## No-cost Windows CPU-first benchmark protocol

1. Pin Windows build, CPU, usable RAM (<=16 GB), integrated GPU, exact model and GGUF SHA256,
   llama.cpp commit/binary hash and runner command. Use the model's actual KV heads, head size,
   layer count and K/V precision; don't infer them from a 7B parameter label.
2. Run documented supported llama.cpp configurations at context sizes 2048, 4096 and 8192
   *only where supported and affordable*; include f16 K/V baseline and other K/V types only
   when the installed engine supports them. Record executable help/feature support.
3. Measure p50/p95 prompt-processing latency, decode tokens/sec, peak process working set
   and end-to-end task success, with three warm and three cold trials, separate prefix cache
   hits/misses, and versioned task fixtures.
4. Record actual per-process RAM and system RAM. Reject experiments when expected peak
   memory plus reserved OS headroom exceeds available RAM. Do not claim KV estimate equals RSS.
5. Compare output consistency/grounding across settings; do not promote a change that saves
   memory but loses held-out answer correctness.
6. Never reuse cache entries across workspace/security boundaries or after source/policy version
   changes. AAK grants and authorization must be verified independently of any cache.
7. Publish raw CSV/JSON, all parameters, tool versions, warm/cold protocol and failures.
   Unsupported configuration -> skipped, not silently counted as passed.

Evaluation targets: APEX Windows runtime, TANDEM verified-context caching, MICA evidence
freshness, FORGE request budgets and AAK authority boundaries. No runtime implementation
or paid GPU resources are part of this change.

References: llama.cpp llama-bench https://github.com/ggml-org/llama.cpp/tree/master/tools/llama-bench
and llama.cpp main repo https://github.com/ggml-org/llama.cpp.
