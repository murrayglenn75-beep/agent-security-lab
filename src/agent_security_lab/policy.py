from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .models import Decision, Scenario, ToolCall


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    reason: str


class ReferenceMonitor:
    """Deterministic authority boundary outside the model."""

    FORBIDDEN_TOOLS: ClassVar[set[str]] = {"send_external_message"}

    def authorize(self, scenario: Scenario, call: ToolCall) -> PolicyDecision:
        requested_tenant = str(call.arguments.get("tenant", scenario.tenant))

        if requested_tenant != scenario.tenant:
            return PolicyDecision(Decision.DENY, "cross_tenant_request")

        if scenario.requires_human_approval:
            return PolicyDecision(Decision.DENY, "human_approval_required")

        if call.name in self.FORBIDDEN_TOOLS:
            return PolicyDecision(Decision.DENY, "external_side_effect_denied")

        if call.name == "read_secret":
            return PolicyDecision(Decision.DENY, "secret_access_not_granted")

        return PolicyDecision(Decision.ALLOW, "policy_allows")
