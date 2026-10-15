# RRSI local evidence verifier

Offline SHA-256 manifest validation for experimental harness improvements. Rejects missing/tampered artifacts, unsafe relative paths, symlinks, mismatched rollback and benchmark identifiers, and candidates rejected by the existing RRSI gate.

**Security boundary:** This verifies file-byte consistency *against the supplied manifest*, not the authenticity of the person producing it. A malicious producer can forge both content and manifest. It does not independently attest held-out test execution, human identity, approval, benchmark isolation, real token costs or rollback success. No autonomous patch application or production promotion is enabled.

To reach the next maturity stage: generate signed provenance and CI-owned reports outside candidate workspaces; execute held-out tests in a network-isolated verifier with hidden answers; link git SHAs to results; demonstrate rollback and replay under failure; require AAK approval independently.
