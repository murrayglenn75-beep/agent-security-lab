from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AttackCategory(StrEnum):
    DIRECT_PROMPT_INJECTION = "direct_prompt_injection"
    INDIRECT_PROMPT_INJECTION = "indirect_prompt_injection"
    SECRET_EXFILTRATION = "secret_exfiltration"
    UNAUTHORIZED_TOOL_USE = "unauthorized_tool_use"
    CROSS_TENANT = "cross_tenant"
    APPROVAL_BYPASS = "approval_bypass"


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class TraceEvent(BaseModel):
    step: int
    event: str
    detail: str


class Scenario(BaseModel):
    id: str
    category: AttackCategory
    severity: str = "high"
    user_input: str
    requested_tool: ToolCall | None = None
    tenant: str = "alpha"
    protected_tenant: str = "alpha"
    requires_human_approval: bool = False
    secret_canary: str = "ASL_CANARY_SECRET"
    expect_attack_contained: bool = True


class AgentResult(BaseModel):
    scenario_id: str
    agent: str
    decision: Decision
    compromise: bool
    secret_leaked: bool
    unauthorized_tool_call: bool
    cross_tenant_violation: bool
    approval_bypass: bool
    output: str
    trace: list[TraceEvent]
