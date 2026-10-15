# Evidence-linked layered memory and RAG evaluation pilot

Offline proof of concept: L0 source conversation, L1 atomic assertions, L2 scenarios, L3 durable derived knowledge. Each node points to exact evidence bytes through workspace-scoped identifier and SHA-256. Recall is simple lexical filtering, not embeddings or production semantic retrieval. Model-generated summaries are not authoritative, and SHA-256 consistency is not proof of truth.

RAG benchmark extension: evaluate missing-evidence abstention and cross-tenant negatives alongside existing Recall@K/MRR/nDCG metrics. The existing evaluator is an *offline scorer*, not a live retrieval system. False-positive assertions must fail independently checked evidence requirements.

Local OCR decision: first compare native PDF text extraction, lightweight local OCR and optional vision OCR with labelled scans/tables; measure field accuracy, table structure, p50/p95 latency and Windows peak RAM <= 16 GB. No models, APIs or paid resources installed by this PR.

Integration targets: TANDEM and MICA persistent memory, APEX local context, FORGE evidence references; all require authoritative project source and independent access control.
