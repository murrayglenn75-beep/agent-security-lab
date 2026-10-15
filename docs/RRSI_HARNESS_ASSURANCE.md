# RRSI-inspired Harness Improvement Assurance Gate

**Experimental advisory prototype**, not recursive autonomous self-modification.

Candidate proposals must provide a small bounded change set, immutable benchmark identifier, paired train and held-out outcomes, token costs, explicit security and leakage checks, independent review, human approval and rollback reference. Repeated failures and attempts to change protected policy, workflow and held-out benchmark paths are rejected. A conservative two-standard-error margin plus a token-cost penalty prevents unconvincing gains from being presented as promotion-ready.

This relies on **caller-supplied metadata**. It does not independently attest tests, approvals, paths, reviewer identity, benchmark independence or rollback feasibility. It is not a substitute for AAK enforcement and cannot authorize patches or deployment. In particular, no model should be given permissions to rewrite its own authority policies or approve its own candidate.

Adoption design:
- APEX: evaluate inspect-plan-patch harness proposals against versioned, never-trained-on held-out tasks with real CPU/RAM cost.
- FORGE: run changes in independently isolated candidate workspaces, log failed fingerprints, exercise restart and replay recovery, and hold independent deployment approval.
- Ethical Hacker: review cross-file impacts and adversarial leakage checks on every candidate, preserving raw evidence.
- Kestrel: calibrate abstention and significance thresholds on disjoint datasets.
- TANDEM: test specialist studio routing before authorizing live use.
- AAK: deterministic enforcement, approvals and audit remain immutable to these experiments.

Source: RRSI Google Research paper/project and screenshot commentary shared 2026-10-15. Reported Terminal-Bench gain is unverified on our infrastructure.
