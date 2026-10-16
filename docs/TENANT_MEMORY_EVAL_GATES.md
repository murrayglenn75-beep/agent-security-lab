# Tenant isolation, eval-first engineering, and persistent memory

## Verified scope in this PR
`src/tenant_isolation.py` is an **in-memory reference guard** and synthetic canary probe.
It demonstrates tenant-first filtering, per-tenant cache keys, and refusal of unsafe fallback.
It does not prove isolation of a real RAG service, BM25, vector database, LLM prompt examples, or distributed cache.

## Production invariants (not implemented here)
1. Derive tenant identity from verified auth context; never let user text supply it.
2. Apply the same immutable tenant filter to vector and BM25 retrieval and reranking.
3. On zero hits, return not-found: never relax the tenant filter.
4. Tenant-scope cache entries, history, prompt examples, embedding stores, and tool output.
5. Perform canary tests via the **same production path users take**, with alert-on-any-hit and strict cleanup.
6. Prevent cross-project memory promotion; every memory record needs scope, source, verifier, creation and expiry timestamps.
7. Test deletion, retention, audit and prompt-injection containment independently.

## Evaluation before modifications
- Create representative failure cases and a held-out test split before a repair.
- Capture baseline accuracy, false-positive rate, tenant leakage rate and run time.
- Define promotion criteria in advance and compare candidates on identical held-out samples.
- For safety tests, require zero cross-tenant leaks; any uncertain test outcome blocks promotion.
- Save only independently verified findings as reusable knowledge. Model-generated summaries remain untrusted hypotheses.

## Three-tier memory target
- Tier 1: minimal, reviewable session-start project instructions. No secrets or unverified assertions.
- Tier 2: local searchable transcript history with explicit retention and deletion.
- Tier 3: optional evidence/provenance-aware semantic retrieval; memory entries remain untrusted and scoped.
- Do not silently store sensitive user information in Git history; use a governed local store with deletion support.
- Measure token use, retrieval precision, deduplication, contamination rate and cold-start latency.
