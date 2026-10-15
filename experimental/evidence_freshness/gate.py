"""Advisory evidence freshness checking; no model memory or authority execution."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

HEX = re.compile(r"[0-9a-f]{64}\Z")
STATUSES = frozenset({"verified", "stale", "disputed", "superseded", "proposed"})


@dataclass(frozen=True)
class Assertion:
    claim_id: str
    workspace_id: str
    source_id: str
    source_version: str
    source_sha256: str
    status: str = "verified"
    supersedes: str | None = None


@dataclass(frozen=True)
class Source:
    workspace_id: str
    source_id: str
    version: str
    data: bytes


@dataclass(frozen=True)
class Freshness:
    status: str
    reason: str


def check(claim: Assertion, sources: dict[tuple[str, str], Source], *, workspace_id: str) -> Freshness:
    """A matching hash means byte-consistent, not factually true or independently trusted."""
    if not workspace_id or claim.workspace_id != workspace_id:
        return Freshness("untrusted", "workspace_mismatch")
    if (not claim.claim_id or not claim.source_id or not claim.source_version
            or not isinstance(claim.source_sha256, str) or not HEX.fullmatch(claim.source_sha256)
            or claim.status not in STATUSES):
        return Freshness("untrusted", "invalid_claim")
    if claim.status != "verified":
        return Freshness("untrusted", "claim_not_verified")
    source = sources.get((workspace_id, claim.source_id))
    if source is None:
        return Freshness("stale", "source_missing")
    if source.workspace_id != workspace_id or source.source_id != claim.source_id:
        return Freshness("untrusted", "source_boundary_mismatch")
    if source.version != claim.source_version:
        return Freshness("stale", "version_changed")
    if not isinstance(source.data, bytes) or hashlib.sha256(source.data).hexdigest() != claim.source_sha256:
        return Freshness("stale", "bytes_changed")
    return Freshness("verified", "same_source_version_and_bytes")


def assess_history(claims: tuple[Assertion, ...], sources: dict[tuple[str, str], Source],
                   *, workspace_id: str) -> dict[str, Freshness]:
    """Old claims preserved, but no conflicting current assertion is trusted."""
    if len({c.claim_id for c in claims}) != len(claims):
        raise ValueError("duplicate claim identifier")
    visible = tuple(c for c in claims if c.workspace_id == workspace_id)
    results = {c.claim_id: check(c, sources, workspace_id=workspace_id) for c in visible}
    referenced = {c.supersedes for c in visible if c.supersedes}
    for claim in visible:
        if claim.claim_id in referenced:
            results[claim.claim_id] = Freshness("untrusted", "superseded_by_newer_assertion")
    current = [c for c in visible if c.claim_id not in referenced and results[c.claim_id].status == "verified"]
    by_source: dict[str, list[Assertion]] = {}
    for claim in current:
        by_source.setdefault(claim.source_id, []).append(claim)
    for group in by_source.values():
        if len(group) > 1:
            for claim in group:
                results[claim.claim_id] = Freshness("untrusted", "unresolved_competing_claims")
    return results
