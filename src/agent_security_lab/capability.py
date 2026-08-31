from __future__ import annotations

import hashlib
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from .models import Decision, ToolCall


class CapabilityGrantSpec(BaseModel):
    """Synthetic capability grant used by the deterministic security lab."""

    model_config = ConfigDict(frozen=True)

    alias: str
    subject: str = "agent"
    tenant: str
    tool: str
    resource: str | None = None
    max_uses: int = Field(default=1, ge=1)
    ttl_steps: int = Field(default=5, ge=1)
    approved: bool = True


class Capability(BaseModel):
    model_config = ConfigDict(frozen=True)

    capability_id: str
    subject: str
    tenant: str
    tool: str
    resource: str | None
    max_uses: int
    issued_step: int
    expires_step: int
    approved: bool


@dataclass(frozen=True)
class CapabilityDecision:
    decision: Decision
    reason: str


class CapabilityBroker:
    """Deterministic capability broker for local adversarial evaluation.

    Capability IDs are reproducible test identifiers, not production bearer tokens.
    """

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
        self._uses: dict[str, int] = {}
        self._counter = 0

    def issue(self, spec: CapabilityGrantSpec, current_step: int) -> Capability:
        self._counter += 1
        raw = (
            f"{self._counter}|{spec.alias}|{spec.subject}|{spec.tenant}|"
            f"{spec.tool}|{spec.resource}|{current_step}"
        ).encode()
        capability_id = "aslcap_" + hashlib.sha256(raw).hexdigest()[:24]
        capability = Capability(
            capability_id=capability_id,
            subject=spec.subject,
            tenant=spec.tenant,
            tool=spec.tool,
            resource=spec.resource,
            max_uses=spec.max_uses,
            issued_step=current_step,
            expires_step=current_step + spec.ttl_steps,
            approved=spec.approved,
        )
        self._capabilities[capability_id] = capability
        self._uses[capability_id] = 0
        return capability

    def authorize_and_consume(
        self,
        capability_id: str | None,
        *,
        actor: str,
        call: ToolCall,
        current_step: int,
    ) -> CapabilityDecision:
        if capability_id is None:
            return CapabilityDecision(Decision.DENY, "capability_missing")

        capability = self._capabilities.get(capability_id)
        if capability is None:
            return CapabilityDecision(Decision.DENY, "capability_unknown")

        if not capability.approved:
            return CapabilityDecision(Decision.DENY, "capability_unapproved")

        if capability.subject != actor:
            return CapabilityDecision(Decision.DENY, "capability_subject_mismatch")

        call_tenant = str(call.arguments.get("tenant", ""))
        if capability.tenant != call_tenant:
            return CapabilityDecision(Decision.DENY, "capability_tenant_mismatch")

        if capability.tool != call.name:
            return CapabilityDecision(Decision.DENY, "capability_tool_mismatch")

        if capability.resource is not None:
            call_resource = str(call.arguments.get("resource", ""))
            if capability.resource != call_resource:
                return CapabilityDecision(
                    Decision.DENY,
                    "capability_resource_scope_mismatch",
                )

        if current_step > capability.expires_step:
            return CapabilityDecision(Decision.DENY, "capability_expired")

        uses = self._uses[capability_id]
        if uses >= capability.max_uses:
            return CapabilityDecision(Decision.DENY, "capability_replay")

        self._uses[capability_id] = uses + 1
        return CapabilityDecision(Decision.ALLOW, "capability_allow")
