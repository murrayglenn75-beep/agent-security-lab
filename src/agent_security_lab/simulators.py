from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RAGDocument:
    key: str
    content: str
    trusted: bool
    source: str


class RAGSimulator:
    """Local deterministic retrieval store with explicit provenance."""

    def __init__(self) -> None:
        self._documents: dict[str, RAGDocument] = {}

    def store(self, document: RAGDocument) -> None:
        self._documents[document.key] = document

    def retrieve(self, key: str) -> RAGDocument | None:
        return self._documents.get(key)


@dataclass(frozen=True)
class MemoryRecord:
    key: str
    content: str
    trusted: bool
    source: str


class MemorySimulator:
    """Session memory that preserves trust/provenance metadata."""

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

    def write(self, record: MemoryRecord) -> None:
        self._records[record.key] = record

    def read(self, key: str) -> MemoryRecord | None:
        return self._records.get(key)
