"""Fail-closed, dependency-free evidence gate for AI-generated research claims.

This validates evidence metadata and status eligibility, not scientific truth.
"""
import hashlib
import re
from dataclasses import dataclass

SHA256 = re.compile(r"^[0-9a-f]{64}$")
STATES = frozenset({"proposed", "reproduced", "independently_checked"})


@dataclass(frozen=True)
class Evidence:
    kind: str
    sha256: str
    source: str
    method: str


@dataclass(frozen=True)
class Claim:
    claim_id: str
    description: str
    source_url: str
    source_version: str
    source_sha256: str
    generated_by: str
    artifacts: tuple[Evidence, ...]
    state: str = "proposed"
    independent_checker: str = ""
    independent_method: str = ""
    human_reviewer: str = ""
    correction_of: str = ""


def assess(claim):
    if not isinstance(claim, Claim):
        raise TypeError("expected Claim")
    reasons = []
    for name in ("claim_id", "description", "source_url", "source_version",
                 "generated_by"):
        if not getattr(claim, name).strip():
            reasons.append("missing_" + name)
    if not SHA256.fullmatch(claim.source_sha256):
        reasons.append("invalid_source_digest")
    if claim.state not in STATES:
        reasons.append("unknown_state")
    if not claim.artifacts:
        reasons.append("missing_artifacts")
    for e in claim.artifacts:
        if not isinstance(e, Evidence) or not e.source or not e.method or not SHA256.fullmatch(e.sha256):
            reasons.append("invalid_artifact")
            break
    if claim.state in {"reproduced", "independently_checked"}:
        if not any(e.kind == "reproduction" for e in claim.artifacts):
            reasons.append("missing_reproduction")
    if claim.state == "independently_checked":
        if not claim.independent_checker or claim.independent_checker == claim.generated_by:
            reasons.append("missing_independent_checker")
        if not claim.independent_method or not claim.human_reviewer:
            reasons.append("missing_review_or_method")
        if not any(e.kind == "independent_check" for e in claim.artifacts):
            reasons.append("missing_independent_evidence")
    if claim.correction_of == claim.claim_id:
        reasons.append("self_referential_correction")
    return {"eligible_state": claim.state if not reasons else "proposed",
            "gate_passed": not reasons, "reasons": sorted(set(reasons))}


def digest_bytes(data):
    if not isinstance(data, bytes):
        raise TypeError("digest requires raw bytes")
    return hashlib.sha256(data).hexdigest()
