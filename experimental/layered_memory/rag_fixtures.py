"""Offline negative RAG fixtures; no retrieval or generation service is invoked."""
from __future__ import annotations

from dataclasses import dataclass

from experimental.rag_eval.evaluate import Case, evaluate


@dataclass(frozen=True)
class RetrievalFixture:
    query_id: str
    workspace: str
    evidence_workspaces: dict[str, str]
    relevant: tuple[str, ...]
    retrieved: tuple[str, ...]
    has_answer: bool


def score(fixtures: tuple[RetrievalFixture, ...]) -> dict[str, float | None]:
    if not fixtures:
        raise ValueError("fixture set required")
    evaluated = []
    abstained = 0
    for f in fixtures:
        if not f.workspace or not f.query_id:
            raise ValueError("missing identity")
        if any(f.evidence_workspaces.get(i) != f.workspace for i in f.retrieved):
            raise ValueError("cross-workspace or unlabelled evidence")
        if not f.has_answer:
            if f.retrieved:
                raise ValueError("unsupported query must abstain in this negative-control fixture")
            abstained += 1
            continue
        if not f.relevant:
            raise ValueError("answerable query missing labels")
        if any(f.evidence_workspaces.get(i) != f.workspace for i in f.relevant):
            raise ValueError("invalid relevance label")
        evaluated.append(Case(f.query_id, f.relevant, f.retrieved))
    result = evaluate(evaluated) if evaluated else {
        "recall_at_k": None, "mrr_at_k": None, "ndcg_at_k": None,
        "citation_precision": None, "claim_support": None, "cases": 0.0,
    }
    return {**result, "unsupported_abstentions": float(abstained)}
