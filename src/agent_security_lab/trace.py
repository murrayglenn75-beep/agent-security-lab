from __future__ import annotations

import hashlib
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict


class SecurityTraceEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int
    event: str
    detail: str
    previous_hash: str
    event_hash: str


def _hash_event(index: int, event: str, detail: str, previous_hash: str) -> str:
    payload = f"{index}|{event}|{detail}|{previous_hash}".encode()
    return hashlib.sha256(payload).hexdigest()


class ImmutableSecurityTrace:
    """Append-only, hash-chained trace with immutable event records."""

    def __init__(self) -> None:
        self._events: list[SecurityTraceEvent] = []

    @property
    def events(self) -> tuple[SecurityTraceEvent, ...]:
        return tuple(self._events)

    @property
    def head(self) -> str:
        return self._events[-1].event_hash if self._events else "GENESIS"

    def append(self, event: str, detail: str) -> SecurityTraceEvent:
        index = len(self._events) + 1
        previous_hash = self.head
        record = SecurityTraceEvent(
            index=index,
            event=event,
            detail=detail,
            previous_hash=previous_hash,
            event_hash=_hash_event(index, event, detail, previous_hash),
        )
        self._events.append(record)
        return record


def verify_trace(events: Sequence[SecurityTraceEvent]) -> bool:
    previous_hash = "GENESIS"
    for expected_index, event in enumerate(events, start=1):
        if event.index != expected_index:
            return False
        if event.previous_hash != previous_hash:
            return False
        expected_hash = _hash_event(
            event.index,
            event.event,
            event.detail,
            event.previous_hash,
        )
        if event.event_hash != expected_hash:
            return False
        previous_hash = event.event_hash
    return True
