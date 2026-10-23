"""Append-only, hash-chained audit log.

Each event stores the hash of the previous one, so deleting or editing a record
breaks the chain and `verify` reports where. Sinks decide where events land: a
local JSONL file here, immutable object or blob storage in the platform adapters.
"""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from tra_core.identity import Principal
from tra_core.schemas import utcnow

GENESIS = "0" * 64

EventType = Literal[
    "tra_created",
    "artefact_read",
    "model_call",
    "tool_call",
    "agent_output",
    "validation_failed",
    "stage_changed",
    "gate_requested",
    "gate_decision",
    "gate_refused",
    "export",
]


class AuditEvent(BaseModel):
    seq: int
    at: str = Field(default_factory=lambda: utcnow().isoformat())
    tra_id: str
    tra_version: int
    stage: str | None
    event_type: EventType
    actor: str  # workload or user subject
    on_behalf_of: str | None = None
    classification: str = "OFFICIAL_SENSITIVE"
    detail: dict[str, Any] = Field(default_factory=dict)
    prev_hash: str
    hash: str = ""

    def compute_hash(self) -> str:
        body = self.model_dump(mode="json", exclude={"hash"})
        return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


class AuditSink(Protocol):
    def append(self, event: AuditEvent) -> None: ...
    def read_all(self) -> list[AuditEvent]: ...


class MemoryAuditSink:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self.events.append(event)

    def read_all(self) -> list[AuditEvent]:
        return list(self.events)


class JsonlAuditSink:
    """Local development sink. Production uses immutable storage in a separate account."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: AuditEvent) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.model_dump_json() + "\n")

    def read_all(self) -> list[AuditEvent]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [AuditEvent.model_validate_json(line) for line in lines if line.strip()]


def digest(value: str | bytes) -> str:
    data = value.encode() if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


class AuditLog:
    def __init__(self, sink: AuditSink) -> None:
        self.sink = sink
        self._lock = threading.Lock()
        existing = sink.read_all()
        self._seq = existing[-1].seq if existing else 0
        self._last_hash = existing[-1].hash if existing else GENESIS

    def record(
        self,
        *,
        tra_id: str,
        tra_version: int,
        stage: str | None,
        event_type: EventType,
        actor: Principal,
        detail: dict[str, Any] | None = None,
        classification: str = "OFFICIAL_SENSITIVE",
    ) -> AuditEvent:
        with self._lock:
            self._seq += 1
            event = AuditEvent(
                seq=self._seq,
                tra_id=tra_id,
                tra_version=tra_version,
                stage=stage,
                event_type=event_type,
                actor=actor.subject,
                on_behalf_of=actor.acting_for,
                classification=classification,
                detail=detail or {},
                prev_hash=self._last_hash,
            )
            event.hash = event.compute_hash()
            self.sink.append(event)
            self._last_hash = event.hash
            return event

    def events_for(self, tra_id: str) -> list[AuditEvent]:
        return [e for e in self.sink.read_all() if e.tra_id == tra_id]


def verify(events: list[AuditEvent]) -> list[str]:
    """Return a list of problems; empty means the chain is intact."""
    problems = []
    prev = GENESIS
    for i, event in enumerate(events):
        if event.prev_hash != prev:
            problems.append(f"event {event.seq}: prev_hash does not match event {events[i - 1].seq if i else 'genesis'}")
        if event.compute_hash() != event.hash:
            problems.append(f"event {event.seq}: content does not match its hash")
        prev = event.hash
    return problems
