"""Deterministic, effect-free validation of recorded agent decisions.

No tool calls, network requests, code execution, or external effects.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TraceStep:
    event_id: str
    request_id: str
    proposed_action: str
    expected_authorized: bool
    observed_authorized: bool

@dataclass(frozen=True)
class ReplayResult:
    accepted: bool
    reason: str
    checked: int

def replay_decisions(steps: tuple[TraceStep, ...], *, maximum: int = 1024) -> ReplayResult:
    if not steps or len(steps) > maximum or maximum <= 0:
        return ReplayResult(False, "invalid_trace_size", 0)
    observed_ids: set[str] = set()
    for index, step in enumerate(steps):
        if not step.event_id or not step.request_id or not step.proposed_action:
            return ReplayResult(False, "invalid_trace_step", index)
        if step.event_id in observed_ids:
            return ReplayResult(False, "duplicate_event_id", index)
        observed_ids.add(step.event_id)
        if type(step.expected_authorized) is not bool or type(step.observed_authorized) is not bool:
            return ReplayResult(False, "invalid_decision", index)
        if step.expected_authorized != step.observed_authorized:
            return ReplayResult(False, "authorization_regression", index + 1)
    return ReplayResult(True, "matched_recorded_expectations_no_effects", len(steps))
