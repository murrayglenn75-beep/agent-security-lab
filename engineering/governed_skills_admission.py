"""Pure skill admission checks; never loads or executes skill scripts."""
import re
from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class SkillManifest:
    skill_id: str
    version: str
    digest: str
    requested_capabilities: frozenset[str]


@dataclass(frozen=True)
class Admission:
    accepted: bool
    reason: str


def admit_skill(
    manifest: SkillManifest,
    payload: bytes,
    approved_digest: str | None,
    approved_capabilities: frozenset[str],
) -> Admission:
    if not manifest.skill_id or not manifest.version:
        return Admission(False, "invalid_identity")
    if not isinstance(payload, bytes):
        return Admission(False, "invalid_payload")
    if not _DIGEST.fullmatch(manifest.digest):
        return Admission(False, "invalid_digest")
    if approved_digest is None or not _DIGEST.fullmatch(approved_digest):
        return Admission(False, "missing_independent_approval")
    if not compare_digest(sha256(payload).hexdigest(), manifest.digest):
        return Admission(False, "content_changed")
    if not compare_digest(manifest.digest, approved_digest):
        return Admission(False, "approval_mismatch")
    if not manifest.requested_capabilities.issubset(approved_capabilities):
        return Admission(False, "capability_expansion")
    return Admission(True, "admitted_for_review_not_execution")
