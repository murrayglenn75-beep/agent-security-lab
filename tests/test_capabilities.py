from pathlib import Path

from agent_security_lab.capability import CapabilityBroker, CapabilityGrantSpec
from agent_security_lab.chain import run_attack_chain
from agent_security_lab.models import Decision, ToolCall


def test_capability_scope_escalation_is_contained() -> None:
    comparison = run_attack_chain(Path("chains/capability_scope_escalation.yaml"))

    assert comparison.vulnerable.compromise is True
    assert comparison.vulnerable.capability_violation is True
    assert comparison.hardened.compromise is False
    assert comparison.hardened.capability_denials == 1
    assert comparison.hardened.capability_scope_attempts == 1


def test_single_use_capability_replay_is_denied() -> None:
    comparison = run_attack_chain(Path("chains/capability_replay.yaml"))

    assert comparison.vulnerable.compromise is True
    assert comparison.hardened.compromise is False
    assert comparison.hardened.capability_replay_attempts == 1
    assert comparison.hardened.capability_denials == 1


def test_capability_is_bound_to_subject() -> None:
    comparison = run_attack_chain(Path("chains/capability_subject_theft.yaml"))

    assert comparison.vulnerable.compromise is True
    assert comparison.hardened.compromise is False
    assert comparison.hardened.capability_denials == 1
    assert "capability_subject_mismatch" in comparison.hardened.output


def test_capability_broker_allows_correct_use_once() -> None:
    broker = CapabilityBroker()
    capability = broker.issue(
        CapabilityGrantSpec(
            alias="test",
            subject="agent",
            tenant="alpha",
            tool="read_record",
            resource="invoice-1",
            max_uses=1,
            ttl_steps=3,
        ),
        current_step=1,
    )
    call = ToolCall(
        name="read_record",
        arguments={"tenant": "alpha", "resource": "invoice-1"},
    )

    first = broker.authorize_and_consume(
        capability.capability_id,
        actor="agent",
        call=call,
        current_step=2,
    )
    replay = broker.authorize_and_consume(
        capability.capability_id,
        actor="agent",
        call=call,
        current_step=3,
    )

    assert first.decision is Decision.ALLOW
    assert replay.decision is Decision.DENY
    assert replay.reason == "capability_replay"


def test_capability_broker_rejects_expired_grant() -> None:
    broker = CapabilityBroker()
    capability = broker.issue(
        CapabilityGrantSpec(
            alias="short-lived",
            subject="agent",
            tenant="alpha",
            tool="read_record",
            resource="invoice-1",
            ttl_steps=1,
        ),
        current_step=1,
    )
    call = ToolCall(
        name="read_record",
        arguments={"tenant": "alpha", "resource": "invoice-1"},
    )
    decision = broker.authorize_and_consume(
        capability.capability_id,
        actor="agent",
        call=call,
        current_step=3,
    )

    assert decision.decision is Decision.DENY
    assert decision.reason == "capability_expired"
