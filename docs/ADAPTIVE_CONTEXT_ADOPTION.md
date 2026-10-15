# Adaptive RAG/CAG context selection (2026-10-15)

An offline, advisory contract chooses **deny**, **rag** (fresh per-query retrieval), or **cag** (preloaded stable context) based on caller-supplied workspace, source verification, freshness, corpus token size, available context window and current-information requirements.

This is not a live retriever, real KV cache, access-control implementation, or correctness guarantee. Unknown/stale sources are denied and only trusted upstream metadata should be provided. AAK authorization must be independently checked for any tool effect.

Integration targets:
- APEX: context-window-aware deterministic local model routing; benchmark Windows <=16GB RAM.
- TANDEM: reuse small stable workspace context and retrieve changing project documents.
- MICA: preserve source-linked layered memory and invalidate CAG materializations when source versions change.
- FORGE: pin static instructions but refresh external state before recovery/retries.
- Brain-AI: hold a labelled comparative eval set for full-context/CAG/RAG/hybrid, with citation support, p50/p95 latency, peak RSS and token costs.
- AAK: never treat cached assertions as grants; check live policy.

Experimental acceptance: independent workspace boundary tests, source freshness, version-based cache invalidation, actual tokenizer budgets, held-out accuracy/faithfulness and measured cache memory. No current production or model integration is implied.
