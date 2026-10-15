"""Offline evidence-linked memory index; never a policy or authorization source."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    node_id: str
    workspace: str
    level: int
    text: str
    evidence_id: str
    evidence_sha256: str
    parent_ids: tuple[str, ...] = ()


def validate(nodes: tuple[Node, ...], evidence: dict[tuple[str, str], bytes], workspace: str) -> None:
    if not workspace or len({node.node_id for node in nodes}) != len(nodes):
        raise ValueError("workspace or duplicate node")
    by_id = {node.node_id: node for node in nodes}
    for node in nodes:
        if (node.workspace != workspace or node.level not in (0, 1, 2, 3)
                or not node.node_id or not node.evidence_id or not node.text):
            raise ValueError("invalid or foreign memory node")
        data = evidence.get((workspace, node.evidence_id))
        if not isinstance(data, bytes) or hashlib.sha256(data).hexdigest() != node.evidence_sha256:
            raise ValueError("missing or changed raw evidence")
        for parent in node.parent_ids:
            referenced = by_id.get(parent)
            if referenced is None or referenced.level >= node.level or referenced.workspace != workspace:
                raise ValueError("invalid memory hierarchy reference")


def recall(nodes: tuple[Node, ...], evidence: dict[tuple[str, str], bytes],
           workspace: str, terms: tuple[str, ...]) -> tuple[Node, ...]:
    validate(nodes, evidence, workspace)
    if not terms or any(not term.strip() for term in terms):
        raise ValueError("nonempty query terms required")
    return tuple(node for node in nodes if any(term.lower() in node.text.lower() for term in terms))
