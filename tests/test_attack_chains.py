from pathlib import Path

from agent_security_lab.chain import run_attack_chain
from agent_security_lab.trace import verify_trace


def test_rag_poison_chain_is_contained_by_hardened_agent() -> None:
    comparison = run_attack_chain(Path("chains/rag_poison_to_secret.yaml"))

    assert comparison.vulnerable.compromise is True
    assert comparison.vulnerable.secret_leaked is True
    assert comparison.hardened.compromise is False
    assert comparison.hardened.contained is True
    assert comparison.hardened.trace_valid is True


def test_memory_poison_chain_cannot_bypass_hardened_approval() -> None:
    comparison = run_attack_chain(Path("chains/memory_poison_to_exfiltration.yaml"))

    assert comparison.vulnerable.compromise is True
    assert comparison.vulnerable.approval_bypass is True
    assert comparison.vulnerable.unauthorized_tool_call is True
    assert comparison.hardened.compromise is False
    assert comparison.hardened.approval_bypass is False


def test_rag_poison_can_persist_into_memory_in_vulnerable_path() -> None:
    comparison = run_attack_chain(Path("chains/rag_memory_persistence.yaml"))

    assert comparison.vulnerable.completed_steps == 5
    assert comparison.vulnerable.secret_leaked is True
    assert comparison.hardened.secret_leaked is False
    assert comparison.hardened.trace_valid is True


def test_hash_chained_trace_detects_tampering() -> None:
    comparison = run_attack_chain(Path("chains/rag_poison_to_secret.yaml"))
    events = list(comparison.hardened.trace)
    assert verify_trace(events) is True

    tampered = list(events)
    tampered[1] = tampered[1].model_copy(update={"detail": "tampered-event"})
    assert verify_trace(tampered) is False
