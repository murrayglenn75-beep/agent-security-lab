# Provider-neutral trace evidence contract

Experimental, dependency-free span schema for embedding, retrieval, context assembly, generation, evaluation, tool and recovery.

Every span has a shared trace ID, unique span ID, bounded parent, millisecond timestamps, outcome and optional provider/model, token and financial metadata. Estimates are deliberately separate from provider-billed values.

Default deny: no raw prompts, retrieved document bodies, auth material, API keys or arbitrary metadata. IDs and provider labels are narrowly validated. Producers must also redact records **before** collection and secure storage, retention and access policies; schema checks alone do not prevent leakage inside an allowed identifier.

**Not implemented:** instrumentation in TANDEM, APEX or FORGE, external tracing backend, independent finance reconciliation, real p95/provider costs, UltraBERT deployment or encoder quality benchmarks.

Model evaluation plan: compare candidate encoders only on the same versioned, authorised corpus using RAG Evaluation Gate Recall@K, MRR, nDCG, claim support and measured CPU/RAM/latency. Classification quality must be measured separately; do not assume distillation gains generalize to retrieval.
