# Experimental RAG evidence evaluation

Synthetic labelled fixtures score Recall@K, MRR@K, binary nDCG@K, citation precision and explicitly human-labelled claim support. Metrics with zero eligible citation or claim labels return null (not evaluated).

This is a **research and regression harness**, not a production RAG pipeline, real model benchmark, truth detector or privacy guarantee. Before adoption: gather a versioned golden set with tenant-scoped permission cases, citations grounded to source spans, forbidden-access negatives, relevant document revisions, measured p50/p95 latency and cost, human adjudication and baseline/candidate comparisons. Do not expose private Brain-AI core or call a passing synthetic test evidence of real-world retrieval quality.
