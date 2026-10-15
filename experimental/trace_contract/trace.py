"""Provider-neutral, privacy-minimal trace span validation."""
from __future__ import annotations

import re
from dataclasses import dataclass

STAGES = frozenset({"embedding", "retrieval", "context", "generation", "evaluation", "tool", "recovery"})
OUTCOMES = frozenset({"ok", "error", "deferred"})
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,96}\Z")
DENIED = ("prompt", "content", "secret", "token_value", "api_key", "password", "authorization", "raw_document")


@dataclass(frozen=True)
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    stage: str
    start_ms: int
    end_ms: int
    outcome: str
    provider_id: str | None = None
    model_version: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None
    billed_cost_usd: float | None = None


def validate(span: Span) -> None:
    for value in (span.trace_id, span.span_id):
        if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
            raise ValueError("invalid trace or span identifier")
    if span.parent_id is not None and (not isinstance(span.parent_id, str) or not SAFE_ID.fullmatch(span.parent_id)):
        raise ValueError("invalid parent identifier")
    if span.parent_id == span.span_id:
        raise ValueError("self-parenting span")
    if span.stage not in STAGES or span.outcome not in OUTCOMES:
        raise ValueError("unrecognized stage or outcome")
    if type(span.start_ms) is not int or type(span.end_ms) is not int or span.start_ms < 0 or span.end_ms < span.start_ms:
        raise ValueError("invalid time range")
    for value in (span.input_tokens, span.output_tokens):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("invalid token count")
    for value in (span.estimated_cost_usd, span.billed_cost_usd):
        if value is not None and (type(value) is not float or not (0 <= value < float("inf"))):
            raise ValueError("invalid cost")
    for value in (span.provider_id, span.model_version):
        if value is not None and (not isinstance(value, str) or not SAFE_ID.fullmatch(value)):
            raise ValueError("unsafe provider/model identifier")


def validate_dict(payload: dict) -> Span:
    if not isinstance(payload, dict):
        raise TypeError("expected trace metadata object")
    fields = set(Span.__dataclass_fields__)
    if set(payload) - fields or any(any(bad in k.lower() for bad in DENIED) for k in payload):
        raise ValueError("unknown or potentially sensitive trace field")
    try:
        span = Span(**payload)
    except TypeError as exc:
        raise ValueError("missing trace metadata") from exc
    validate(span)
    return span


def validate_trace(spans: list[Span]) -> None:
    if not spans:
        raise ValueError("empty trace")
    by_id = {}
    trace_id = spans[0].trace_id
    for span in spans:
        validate(span)
        if span.trace_id != trace_id or span.span_id in by_id:
            raise ValueError("mixed traces or duplicate span")
        by_id[span.span_id] = span
    for span in spans:
        if span.parent_id is not None:
            parent = by_id.get(span.parent_id)
            if parent is None or parent.start_ms > span.start_ms or parent.end_ms < span.end_ms:
                raise ValueError("unbounded or missing parent")
            visited = {span.span_id}
            current = parent
            while current is not None:
                if current.span_id in visited:
                    raise ValueError("cyclic spans")
                visited.add(current.span_id)
                current = by_id.get(current.parent_id) if current.parent_id else None
