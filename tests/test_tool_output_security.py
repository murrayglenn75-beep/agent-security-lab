from pathlib import Path

from agent_security_lab.chain import run_attack_chain
from agent_security_lab.models import Decision, ToolCall
from agent_security_lab.tool_responses import (
    ToolOutputReferenceMonitor,
    ToolResponseSimulator,
)


def test_malicious_tool_response_secret_attack_is_contained() -> None:
    comparison = run_attack_chain(
        Path("chains/malicious_tool_response_to_secret.yaml")
    )

    assert comparison.vulnerable.compromise is True
    assert comparison.vulnerable.secret_leaked is True
    assert comparison.vulnerable.tool_output_violation is True

    assert comparison.hardened.compromise is False
    assert comparison.hardened.secret_leaked is False
    assert comparison.hardened.tool_output_denials == 1
    assert "untrusted_tool_output_cannot_grant_authority" in (
        comparison.hardened.output
    )
    assert comparison.hardened.trace_valid is True


def test_confused_deputy_external_action_is_contained() -> None:
    comparison = run_attack_chain(
        Path("chains/confused_deputy_tool_response.yaml")
    )

    assert comparison.vulnerable.compromise is True
    assert comparison.vulnerable.approval_bypass is True
    assert comparison.vulnerable.tool_output_violation is True

    assert comparison.hardened.compromise is False
    assert comparison.hardened.approval_bypass is False
    assert comparison.hardened.tool_output_denials == 1


def test_tool_output_cannot_expand_capability_scope() -> None:
    comparison = run_attack_chain(
        Path("chains/tool_response_capability_escalation.yaml")
    )

    assert comparison.vulnerable.compromise is True
    assert comparison.vulnerable.capability_violation is True
    assert comparison.vulnerable.tool_output_violation is True

    assert comparison.hardened.compromise is False
    assert comparison.hardened.tool_output_denials == 0
    assert comparison.hardened.capability_denials == 1
    assert comparison.hardened.capability_scope_attempts == 1
    assert "capability_resource_scope_mismatch" in comparison.hardened.output


def test_tool_response_simulator_preserves_provenance() -> None:
    simulator = ToolResponseSimulator()
    response = simulator.respond(
        tool="search_connector",
        content="synthetic hostile content",
        trusted=False,
        source="compromised_connector",
    )

    assert response.tool == "search_connector"
    assert response.content == "synthetic hostile content"
    assert response.trusted is False
    assert response.source == "compromised_connector"


def test_tool_output_monitor_defers_to_independent_capability() -> None:
    simulator = ToolResponseSimulator()
    response = simulator.respond(
        tool="records_plugin",
        content="read another record",
        trusted=False,
        source="compromised_plugin",
    )
    decision = ToolOutputReferenceMonitor().authorize(
        response=response,
        call=ToolCall(
            name="read_record",
            arguments={"tenant": "alpha", "resource": "invoice-2"},
        ),
        capability_ref="invoice-one",
    )

    assert decision.decision is Decision.ALLOW
    assert decision.reason == "independent_capability_required"
