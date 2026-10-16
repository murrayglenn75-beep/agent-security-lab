"""Fail-closed tenant-scoped retrieval primitives for security experiments.

Caller must supply a trusted tenant identity from authentication, never from
prompt text. This module is a reference guard, not an auth provider.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Callable, Iterable

@dataclass(frozen=True)
class Chunk:
    tenant_id: str
    doc_id: str
    text: str

def _tenant(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise ValueError("invalid_authenticated_tenant")
    return value

def search_scoped(authenticated_tenant: str, chunks: Iterable[Chunk],
                  match: Callable[[str], bool]) -> list[Chunk]:
    """Filter BEFORE scoring or search; do not retry without this predicate."""
    tenant = _tenant(authenticated_tenant)
    return [c for c in chunks if isinstance(c, Chunk) and
            c.tenant_id == tenant and match(c.text)]

def cache_key(authenticated_tenant: str, question: str) -> str:
    tenant = _tenant(authenticated_tenant)
    if not isinstance(question, str) or len(question) > 8192:
        raise ValueError("invalid_question")
    return sha256((str(len(tenant)) + ":" + tenant + ":" + question).encode("utf-8")).hexdigest()

def canary_probe(chunks: Iterable[Chunk], source_tenant: str,
                 target_tenant: str, phrase: str) -> dict:
    source = _tenant(source_tenant)
    target = _tenant(target_tenant)
    if source == target:
        raise ValueError("canary_tenants_must_differ")
    if not isinstance(phrase, str) or len(phrase) < 8:
        raise ValueError("invalid_canary")
    records = tuple(chunks)
    planted = any(c.tenant_id == source and phrase in c.text for c in records)
    if not planted:
        raise ValueError("canary_not_planted")
    hits = search_scoped(target, records, lambda content: phrase in content)
    return {"source_tenant": source, "target_tenant": target,
            "leak_detected": bool(hits), "hit_count": len(hits),
            "test_scope": "in_memory_reference_only"}
