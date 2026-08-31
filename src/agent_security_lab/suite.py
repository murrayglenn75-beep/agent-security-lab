from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from .metrics import SecurityMetrics, calculate_metrics
from .models import AgentResult
from .runner import run_comparison
from .scenario import load_scenario


class SuiteResult(BaseModel):
    scenario_count: int
    vulnerable: SecurityMetrics
    hardened: SecurityMetrics
    vulnerable_results: list[AgentResult]
    hardened_results: list[AgentResult]


def run_suite(directory: Path) -> SuiteResult:
    scenario_paths = sorted(directory.glob("*.yaml"))
    vulnerable_results: list[AgentResult] = []
    hardened_results: list[AgentResult] = []

    for path in scenario_paths:
        comparison = run_comparison(load_scenario(path))
        vulnerable_results.append(comparison.vulnerable)
        hardened_results.append(comparison.hardened)

    return SuiteResult(
        scenario_count=len(scenario_paths),
        vulnerable=calculate_metrics(vulnerable_results),
        hardened=calculate_metrics(hardened_results),
        vulnerable_results=vulnerable_results,
        hardened_results=hardened_results,
    )
