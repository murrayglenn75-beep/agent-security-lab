"""Label-based RAG retrieval metrics; not an automatic truth oracle."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    question_id: str
    relevant_ids: tuple[str, ...]
    retrieved_ids: tuple[str, ...]
    cited_ids: tuple[str, ...] = ()
    supported_claims: int = 0
    total_claims: int = 0

def evaluate(cases: list[Case], k: int = 5) -> dict[str, float | None]:
    if not cases or type(k) is not int or k < 1:
        raise ValueError("nonempty cases and positive k required")
    recall = mrr = ndcg = citation = support = 0.0
    citation_n = claims_n = 0
    for c in cases:
        relevant = set(c.relevant_ids)
        if not c.question_id or not relevant or len(relevant) != len(c.relevant_ids):
            raise ValueError("relevant IDs must be unique and nonempty")
        if len(c.retrieved_ids) != len(set(c.retrieved_ids)) or len(c.cited_ids) != len(set(c.cited_ids)):
            raise ValueError("duplicate retrieved or cited ID")
        if type(c.supported_claims) is not int or type(c.total_claims) is not int or not 0 <= c.supported_claims <= c.total_claims:
            raise ValueError("invalid claim labels")
        hits = [int(x in relevant) for x in c.retrieved_ids[:k]]
        recall += sum(hits) / len(relevant)
        mrr += next((1/(i+1) for i, hit in enumerate(hits) if hit), 0.0)
        dcg = sum(hit/math.log2(i+2) for i, hit in enumerate(hits))
        ideal = sum(1/math.log2(i+2) for i in range(min(k, len(relevant))))
        ndcg += dcg / ideal
        if c.cited_ids:
            citation_n += 1
            citation += sum(x in relevant and x in c.retrieved_ids for x in c.cited_ids)/len(c.cited_ids)
        if c.total_claims:
            claims_n += 1
            support += c.supported_claims/c.total_claims
    n = len(cases)
    return {"recall_at_k":recall/n, "mrr_at_k":mrr/n, "ndcg_at_k":ndcg/n,
            "citation_precision":citation/citation_n if citation_n else None,
            "claim_support":support/claims_n if claims_n else None,
            "cases":float(n)}
