# APEX CPU-first KV-cache measurement plan

Analytical estimator, not runtime benchmark. Formula is L * T * KV_heads * head_dim * (key bytes + value bytes) * concurrent sequences. Actual runtime footprint also depends on model weights, buffers, allocation padding, context slots, architecture, KV types, shared layers, paging and OS overhead.

On the target Windows <=16 GiB machine:
1. Pin llama.cpp release/commit and GGUF SHA256; record CPU, RAM, Windows version and model architecture.
2. Confirm supported key/value cache types and use runtime-reported values rather than assuming that a given quantization saves exactly 50%.
3. Run fixed, repeatable prompts at context lengths 2048, 4096 and 8192 **only if supported**; use cold and warm runs, fixed output lengths, and latency/throughput measurement with llama-bench and an external peak-process-memory monitor.
4. Report prompt tokens/s, generation tokens/s, p50/p95 per-request latency, peak RAM, correctness/citation quality and crash/timeout counts.
5. Compare default FP16 KV, supported compact KV, and prompt-prefix reuse only if the installed backend implements each setting. Never infer correctness or faster inference from cache capacity.
6. Reject settings exceeding available RAM and preserve independent security permissions before any adoption.

The source screenshots explain conventional decoder KV reuse and why context memory grows. Multi-layer/GQA/MLA architectures have different cache formulas. This prototype does not modify APEX, TANDEM, llama.cpp or model weights, and no Windows measurement was performed.
