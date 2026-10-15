"""Local evidence integrity checks for offline RRSI experiments; no execution permissions."""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath

from experimental.rrsi_gate.gate import Candidate, Verdict, assess

MAX_BYTES = 2_000_000


def verify_bundle(root: Path, manifest: dict, candidate: Candidate) -> Verdict:
    """Read immutable-ish local files and compare digests; metadata signatures remain unverified."""
    errors = []
    if type(manifest) is not dict or set(manifest) != {"benchmark_id", "artifacts", "rollback"}:
        return Verdict(False, ("invalid_manifest",))
    if manifest["benchmark_id"] != candidate.benchmark_id or manifest["rollback"] != candidate.rollback_reference:
        errors.append("manifest_mismatch")
    files = manifest["artifacts"]
    if type(files) is not dict or not files or len(files) > 30:
        return Verdict(False, ("invalid_artifacts",))
    root = root.resolve()
    for name, digest in files.items():
        if type(name) is not str or type(digest) is not str:
            errors.append("invalid_artifact")
            continue
        p = PurePosixPath(name)
        if (not name or p.is_absolute() or ".." in p.parts or "\\" in name
                or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest)):
            errors.append("invalid_artifact")
            continue
        target = root.joinpath(*p.parts)
        try:
            if target.is_symlink() or not target.resolve().is_relative_to(root) or not target.is_file():
                raise ValueError("unsafe artifact")
            if target.stat().st_size > MAX_BYTES:
                raise ValueError("artifact too large")
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
        except (OSError, ValueError):
            errors.append("unreadable_artifact")
            continue
        if actual != digest:
            errors.append("artifact_hash_mismatch")
    gate = assess(candidate)
    return Verdict(not errors and gate.eligible, tuple(dict.fromkeys((*errors, *gate.reasons))))


def manifest_for(files: dict[str, bytes], benchmark_id: str, rollback: str) -> dict:
    """Test helper only: caller controls content, never an independent attestation."""
    return {"benchmark_id": benchmark_id, "rollback": rollback,
            "artifacts": {p: hashlib.sha256(b).hexdigest() for p, b in files.items()}}
