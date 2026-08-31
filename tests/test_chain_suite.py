import json
from pathlib import Path

from agent_security_lab.chain_suite import (
    discover_attack_chains,
    run_chain_suite,
    write_chain_suite_reports,
)


def test_expanded_chain_corpus_has_at_least_40_cases() -> None:
    paths = discover_attack_chains(Path("chains"))
    assert len(paths) >= 40


def test_full_chain_suite_contains_all_attacks() -> None:
    summary = run_chain_suite(Path("chains")).summary

    assert summary.total_chains >= 40
    assert summary.vulnerable_compromises == summary.total_chains
    assert summary.vulnerable_attack_success_rate == 100.0


def test_full_chain_suite_hardened_path_contains_all_attacks() -> None:
    summary = run_chain_suite(Path("chains")).summary

    assert summary.hardened_compromises == 0
    assert summary.hardened_attack_success_rate == 0.0
    assert summary.hardened_containment_rate == 100.0
    assert summary.severity_weighted_residual_risk == 0
    assert summary.severity_weighted_risk_reduction == 100.0


def test_full_chain_suite_all_traces_verify() -> None:
    summary = run_chain_suite(Path("chains")).summary
    assert summary.trace_valid_rate == 100.0


def test_chain_suite_is_deterministic() -> None:
    first = run_chain_suite(Path("chains")).summary
    second = run_chain_suite(Path("chains")).summary
    assert first == second


def test_chain_suite_reports_include_json_jsonl_and_html(tmp_path: Path) -> None:
    run = run_chain_suite(Path("chains"))
    paths = write_chain_suite_reports(run, tmp_path)

    summary_payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary_payload["schema_version"] == "1.1"
    assert summary_payload["total_chains"] >= 40

    jsonl_lines = paths.trace_jsonl.read_text(encoding="utf-8").splitlines()
    assert len(jsonl_lines) > run.summary.total_chains * 2
    first_trace = json.loads(jsonl_lines[0])
    assert first_trace["schema_version"] == "1.1"
    assert "trace_head" in first_trace
    assert "event" in first_trace

    html = paths.html_report.read_text(encoding="utf-8")
    assert "Agent Security Lab v1.1" in html
    assert "Weighted risk reduction" in html


def test_suite_observes_capability_abuse_signals() -> None:
    summary = run_chain_suite(Path("chains")).summary
    assert summary.capability_denials > 0
    assert summary.capability_replay_attempts > 0
    assert summary.capability_scope_attempts > 0
