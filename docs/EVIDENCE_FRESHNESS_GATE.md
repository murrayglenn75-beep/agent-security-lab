# Evidence Freshness Gate — experimental

Deterministic comparison of claim source version and SHA-256 with current source bytes, with workspace scoping, visible supersession and conservative conflicting-claim handling.

**Verified means source-byte consistency only**; it is not factual truth, independent verification, source authenticity, a trusted source registry, tenant access-control enforcement, or an authorization grant. Callers cannot use this prototype to substitute for AAK approvals. Supersession relations are metadata and require authenticated provenance before real use. Concurrent versions, arbitrary new sources, forged statuses, privacy retention and source deletions need hardened storage and audit beyond this module.

Adoption targets:
- TANDEM/MICA: persist versioned evidence references, query only live eligible claims after trusted workspace checks; preserve revision history.
- APEX: link engineering assertions to specific file bytes and source commits, invalidate on changes.
- FORGE: invalidate old task assumptions before resuming after code/state changes.
- AAK: independently reauthorize on any material change; never trust a freshness label as permission.
- Brain-AI: attach provenance and freshness reports to research claims.

Next: real trusted source resolver, Git commit attestations, ACL enforcement outside this scorer, independent adjudication, multi-hop graph provenance and replayable migration tests.
