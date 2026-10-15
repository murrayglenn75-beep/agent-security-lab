# RoPE reference and APEX evaluation plan

The Python reference illustrates paired rotary transformations and tests zero-position identity, norm preservation and relative-position invariance of Q-K dot products. This is **not** a deployable attention kernel, model-weight modification, llama.cpp integration or an extended-context quality benchmark.

APEX Windows CPU-first benchmark (planned, not executed):
1. Record Windows version, CPU/iGPU, RAM available, llama.cpp commit, model SHA256, quantization, context configuration and RoPE scaling settings.
2. Use fixed, versioned needle-in-haystack and document-grounded tasks at several context lengths, with held-out prompts and evidence positions.
3. Measure exact-match/citation accuracy, retrieval failure, p50/p95 prefill and decode latency, process peak working set and CPU utilization; repeat runs with cold/warm cache separated.
4. Compare unmodified model defaults against supported context configurations within model limits; never presume RoPE scaling beyond training length preserves accuracy.
5. Fail the adoption gate on excessive RAM, answer degradation, unsupported source claims or permission leakage. Do not use paid hosting.

Research reference: Su et al., RoFormer: Enhanced Transformer with Rotary Position Embedding (2021), https://arxiv.org/abs/2104.09864.

Do not infer that this educational reference proves any change to TANDEM, Brain-AI or APEX runtime.
