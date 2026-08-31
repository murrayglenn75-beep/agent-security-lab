from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .capability import CapabilityGrantSpec
from .models import ToolCall
from .trace import SecurityTraceEvent


class ChainStepKind(StrEnum):
    RAG_STORE = "rag_store"
    RAG_RETRIEVE = "rag_retrieve"
    MEMORY_WRITE = "memory_write"
    MEMORY_READ = "memory_read"
    ISSUE_CAPABILITY = "issue_capability"
    PROPOSE_TOOL = "propose_tool"


class AttackChainStep(BaseModel):
    id: str
    kind: ChainStepKind
    source: str = "attacker"
    actor: str = "agent"
    key: str | None = None
    content: str | None = None
    trusted: bool = False
    tool: ToolCall | None = None
    capability: CapabilityGrantSpec | None = None
    capability_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackChainScenario(BaseModel):
    id: str
    severity: str = "critical"
    tenant: str = "alpha"
    protected_tenant: str = "alpha"
    secret_canary: str = "ASL_CANARY_SECRET"
    requires_human_approval: bool = False
    expect_attack_contained: bool = True
    steps: list[AttackChainStep]


class ChainResult(BaseModel):
    scenario_id: str
    agent: str
    compromise: bool
    contained: bool
    secret_leaked: bool
    unauthorized_tool_call: bool
    cross_tenant_violation: bool
    approval_bypass: bool
    capability_violation: bool
    capability_denials: int
    capability_replay_attempts: int
    capability_scope_attempts: int
    completed_steps: int
    total_steps: int
    output: str
    trace_valid: bool
    trace_head: str
    trace: list[SecurityTraceEvent]
