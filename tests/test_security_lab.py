from pathlib import Path

from agent_security_lab.evaluator import evaluate_result
from agent_security_lab.metrics import calculate_metrics
from agent_security_lab.models import AgentResult, Decision
from agent_security_lab.runner import build_default_tools, run_comparison
from agent_security_lab.scenario import load_scenario
from agent_security_lab.suite import run_suite


def test_direct_prompt_injection_is_contained_by_hardened_agent() -> None:
    scenario = load_scenario(Path("scenarios/direct_prompt_injection.yaml"))
    result = run_comparison(scenario)

    assert result.vulnerable.compromise is True
    assert result.vulnerable.secret_leaked is True
    assert result.hardened.compromise is False
    assert result.hardened.secret_leaked is False


def test_cross_tenant_attempt_is_detected_independently() -> None:
    scenario = load_scenario(Path("scenarios/cross_tenant.yaml"))
    result = run_comparison(scenario)

    assert result.vulnerable.cross_tenant_violation is True
    assert result.vulnerable.secret_leaked is True
    assert result.hardened.cross_tenant_violation is False
    assert result.hardened.secret_leaked is False
    assert result.hardened.decision is Decision.DENY


def test_human_approval_bypass_is_contained() -> None:
    scenario = load_scenario(Path("scenarios/approval_bypass.yaml"))
    result = run_comparison(scenario)

    assert result.vulnerable.approval_bypass is True
    assert result.hardened.approval_bypass is False
    assert result.hardened.decision is Decision.DENY


def test_indirect_prompt_injection_is_contained() -> None:
    scenario = load_scenario(Path("scenarios/indirect_prompt_injection.yaml"))
    result = run_comparison(scenario)

    assert result.vulnerable.compromise is True
    assert result.hardened.compromise is False


def test_unauthorized_external_side_effect_is_contained() -> None:
    scenario = load_scenario(Path("scenarios/unauthorized_tool_use.yaml"))
    result = run_comparison(scenario)

    assert result.vulnerable.unauthorized_tool_call is True
    assert result.hardened.unauthorized_tool_call is False


def test_evaluator_overrides_false_safe_agent_claims() -> None:
    scenario = load_scenario(Path("scenarios/direct_prompt_injection.yaml"))
    tools = build_default_tools(scenario.secret_canary)
    leaked = tools.execute("read_secret", {"tenant": "alpha"})

    claimed_safe = AgentResult(
        scenario_id=scenario.id,
        agent="untrusted-test-agent",
        decision=Decision.ALLOW,
        compromise=False,
        secret_leaked=False,
        unauthorized_tool_call=False,
        cross_tenant_violation=False,
        approval_bypass=False,
        output=leaked,
        trace=[],
    )
    evaluated = evaluate_result(scenario, claimed_safe, tools)

    assert evaluated.compromise is True
    assert evaluated.secret_leaked is True
    assert evaluated.unauthorized_tool_call is True


def test_evaluator_can_clear_false_compromise_claims() -> None:
    scenario = load_scenario(Path("scenarios/direct_prompt_injection.yaml"))
    tools = build_default_tools(scenario.secret_canary)

    claimed_compromised = AgentResult(
        scenario_id=scenario.id,
        agent="untrusted-test-agent",
        decision=Decision.DENY,
        compromise=True,
        secret_leaked=True,
        unauthorized_tool_call=True,
        cross_tenant_violation=True,
        approval_bypass=True,
        output="DENIED",
        trace=[],
    )
    evaluated = evaluate_result(scenario, claimed_compromised, tools)

    assert evaluated.compromise is False
    assert evaluated.secret_leaked is False
    assert evaluated.unauthorized_tool_call is False


def test_suite_benchmark_separates_vulnerable_and_hardened_agents() -> None:
    suite = run_suite(Path("scenarios"))

    assert suite.scenario_count == 6
    assert suite.vulnerable.compromises == 6
    assert suite.vulnerable.attack_success_rate == 100.0
    assert suite.hardened.compromises == 0
    assert suite.hardened.attack_success_rate == 0.0


def test_hardened_metrics_are_deterministic() -> None:
    suite = run_suite(Path("scenarios"))
    metrics = calculate_metrics(suite.hardened_results)

    assert metrics.total == 6
    assert metrics.compromises == 0
    assert metrics.attack_success_rate == 0.0
    assert metrics.secret_leakage_rate == 0.0
    assert metrics.unauthorized_tool_call_rate == 0.0



def test_html_report_is_generated(tmp_path: Path) -> None:
    from agent_security_lab.reporting import write_html_report

    suite = run_suite(Path("scenarios"))
    report = write_html_report(suite, tmp_path / "benchmark.html")

    html = report.read_text(encoding="utf-8")
    assert "Agent Security Lab" in html
    assert "Independent evaluator" not in html
    assert "0.00%" in html
    assert "not a claim of universal" in html
