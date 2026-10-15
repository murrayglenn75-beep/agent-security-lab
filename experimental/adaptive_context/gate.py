"""Fail-closed advisory RAG/CAG selection based on trusted metadata."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextRequest:
    workspace: str
    source_workspace: str
    source_verified: bool
    source_fresh: bool
    corpus_tokens: int
    context_budget: int
    source_count: int
    changing: bool
    requires_current_evidence: bool
    prepared_context_available: bool

@dataclass(frozen=True)
class Decision:
    strategy: str
    reason: str

def choose(r: ContextRequest) -> Decision:
    """Never authorizes disclosure; caller must enforce independent access controls."""
    if not r.workspace or r.workspace != r.source_workspace or r.source_verified is not True:
        return Decision("deny", "unverified_workspace_or_source")
    if r.source_fresh is not True:
        return Decision("deny", "stale_or_unknown_source")
    if (type(r.corpus_tokens) is not int or type(r.context_budget) is not int
        or type(r.source_count) is not int or r.corpus_tokens < 0
        or r.context_budget <= 0 or r.source_count < 1):
        return Decision("deny", "invalid_capacity_metadata")
    if r.requires_current_evidence or r.changing or r.corpus_tokens > r.context_budget:
        return Decision("rag", "query_retrieval_required")
    if r.prepared_context_available is True:
        return Decision("cag", "stable_authorized_context_fits")
    return Decision("rag", "no_verified_prepared_context")
