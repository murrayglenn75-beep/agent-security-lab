from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from .models import Decision, ToolCall


class ToolResponse(BaseModel):
    """A deterministic tool response with explicit provenance."""

    model_config = ConfigDict(frozen=True)

    tool: str
    content: str
    trusted: bool
    source: str


class ToolOutputDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision: Decision
    reason: str


class ToolResponseSimulator:
    """Local simulator for tool/plugin responses used in adversarial chains."""

    def respond(
        self,
        *,
        tool: str,
        content: str,
        trusted: bool,
        source: str,
    ) -> ToolResponse:
        return ToolResponse(
            tool=tool,
            content=content,
            trusted=trusted,
            source=source,
        )


class ToolOutputReferenceMonitor:
    """Prevents tool-returned text from becoming authority by itself.

    Untrusted tool output may provide data, but it cannot independently authorize
    privileged actions. Scoped read_record actions may proceed to the separate
    capability monitor, which must authorize them independently.
    """

    _PRIVILEGED_TOOLS: ClassVar[set[str]] = {
        "read_secret",
        "read_record",
        "send_external_message",
    }

    def authorize(
        self,
        *,
        response: ToolResponse | None,
        call: ToolCall,
        capability_ref: str | None,
    ) -> ToolOutputDecision:
        if response is None or response.trusted:
            return ToolOutputDecision(decision=Decision.ALLOW, reason="no_untrusted_tool_output")

        if call.name not in self._PRIVILEGED_TOOLS:
            return ToolOutputDecision(decision=Decision.ALLOW, reason="non_privileged_action")

        if call.name == "read_record" and capability_ref is not None:
            return ToolOutputDecision(
                decision=Decision.ALLOW,
                reason="independent_capability_required",
            )

        return ToolOutputDecision(
            decision=Decision.DENY,
            reason="untrusted_tool_output_cannot_grant_authority",
        )
