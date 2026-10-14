"""Offline evaluation of relationship retrieval and guarded continuation states."""
from __future__ import annotations

from dataclasses import dataclass

from experimental.rag_eval.evaluate import Case, evaluate


@dataclass(frozen=True)
class RelationCase:
    question_id: str
    workspace_id: str
    relevant_ids: tuple[str, ...]
    baseline_ids: tuple[str, ...]
    graph_ids: tuple[str, ...]
    document_workspaces: dict[str, str]


def compare(cases: list[RelationCase], k: int = 5) -> dict[str, dict[str, float | None]]:
    if not cases:
        raise ValueError("labelled cases required")
    baseline: list[Case] = []
    graph: list[Case] = []
    for c in cases:
        if not c.workspace_id:
            raise ValueError("workspace required")
        for ids in (c.relevant_ids, c.baseline_ids, c.graph_ids):
            if any(c.document_workspaces.get(i) != c.workspace_id for i in ids):
                raise ValueError("cross-workspace document encountered; deny evaluation")
        baseline.append(Case(c.question_id, c.relevant_ids, c.baseline_ids))
        graph.append(Case(c.question_id, c.relevant_ids, c.graph_ids))
    return {"baseline": evaluate(baseline, k), "graph": evaluate(graph, k)}


@dataclass(frozen=True)
class Continuation:
    task_id: str
    provider_id: str
    state: str
    deadline_epoch: int
    attempts: int
    max_attempts: int
    authorization_valid: bool
    effects_reconciled: bool
    continuation_reference: str | None = None


def can_resume(task: Continuation, *, now_epoch: int, provider_id: str) -> bool:
    """Advisory fail-closed check, not a distributed lock or authorization grant."""
    if type(now_epoch) is not int:
        return False
    return (
        bool(task.task_id)
        and bool(task.provider_id)
        and provider_id == task.provider_id
        and task.state == "suspended"
        and type(task.deadline_epoch) is int
        and now_epoch < task.deadline_epoch
        and type(task.attempts) is int
        and type(task.max_attempts) is int
        and 0 <= task.attempts < task.max_attempts
        and task.authorization_valid is True
        and task.effects_reconciled is True
        and bool(task.continuation_reference)
    )
