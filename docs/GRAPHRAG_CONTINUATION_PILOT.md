# GraphRAG and continuation adoption pilot — 2026-10-14

Two dependency-free **offline** contracts, not a live GraphRAG or long-running inference runtime:

- **Relationship retrieval comparison:** compare fixed, labelled baseline and graph result IDs through the merged RAG evaluator, refusing any source whose workspace mapping is missing or mismatched. This does not enforce real service authorization: use database RLS / trusted pre-retrieval authorization in an actual deployment.
- **Guarded continuation:** require matching provider, suspended state, unexpired deadline, remaining attempts, validated authorization, reconciled side-effects and an opaque continuation reference. Caller booleans are untrusted without actual independent policy and effect reconciliation.

Before production: run real multi-hop corpora, negative tenant-access cases, citation/faithfulness adjudication, latency/RAM/cost tests; add durable state storage, leases/fencing/idempotency, signed provider provenance, validated expiry and replay prevention. Never store live continuation tokens in logs or project docs.

Source research: EdgeQuake GraphRAG and Gemini 4 Argon Long Decode screenshots (third-party reported capabilities and benchmark figures are unverified). FORGE, TANDEM/MICA and APEX have no runtime changes from this pilot.
