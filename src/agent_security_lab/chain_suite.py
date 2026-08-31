from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .chain import ChainComparisonResult, run_attack_chain

_SEVERITY_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class ChainCaseSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_id: str
    path: str
    severity: str
    total_steps: int
    vulnerable_compromise: bool
    hardened_compromise: bool
    hardened_contained: bool
    vulnerable_secret_leak: bool
    hardened_secret_leak: bool
    hardened_capability_denials: int
    hardened_replay_attempts: int
    hardened_scope_attempts: int
    vulnerable_trace_valid: bool
    hardened_trace_valid: bool
    first_hardened_denial_trace_index: int | None


class ChainSuiteSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: str = "1.1"
    total_chains: int
    vulnerable_compromises: int
    hardened_compromises: int
    vulnerable_attack_success_rate: float
    hardened_attack_success_rate: float
    hardened_containment_rate: float
    trace_valid_rate: float
    capability_denials: int
    capability_replay_attempts: int
    capability_scope_attempts: int
    mean_denial_trace_index: float | None
    severity_weighted_baseline_risk: int
    severity_weighted_residual_risk: int
    severity_weighted_risk_reduction: float
    cases: list[ChainCaseSummary]


@dataclass(frozen=True)
class ChainSuiteRun:
    summary: ChainSuiteSummary
    comparisons: tuple[tuple[Path, ChainComparisonResult], ...]


@dataclass(frozen=True)
class ChainSuiteReportPaths:
    summary_json: Path
    trace_jsonl: Path
    html_report: Path


def discover_attack_chains(chains_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in chains_dir.rglob("*.yaml")
        if path.is_file()
    )


def _first_denial_trace_index(comparison: ChainComparisonResult) -> int | None:
    for event in comparison.hardened.trace:
        if event.event == "tool_denied":
            return event.index
    return None


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 2)


def run_chain_suite(chains_dir: Path) -> ChainSuiteRun:
    paths = discover_attack_chains(chains_dir)
    comparisons: list[tuple[Path, ChainComparisonResult]] = []
    cases: list[ChainCaseSummary] = []

    vulnerable_compromises = 0
    hardened_compromises = 0
    contained_attacks = 0
    vulnerable_attack_cases = 0
    valid_traces = 0
    total_traces = 0
    denial_indices: list[int] = []
    capability_denials = 0
    capability_replay_attempts = 0
    capability_scope_attempts = 0
    baseline_risk = 0
    residual_risk = 0

    for path in paths:
        comparison = run_attack_chain(path)
        comparisons.append((path, comparison))

        vulnerable = comparison.vulnerable
        hardened = comparison.hardened
        severity = comparison.scenario.severity.lower()
        weight = _SEVERITY_WEIGHT.get(severity, 2)

        if vulnerable.compromise:
            vulnerable_compromises += 1
            vulnerable_attack_cases += 1
            baseline_risk += weight
            if not hardened.compromise:
                contained_attacks += 1

        if hardened.compromise:
            hardened_compromises += 1
            residual_risk += weight

        valid_traces += int(vulnerable.trace_valid) + int(hardened.trace_valid)
        total_traces += 2

        capability_denials += hardened.capability_denials
        capability_replay_attempts += hardened.capability_replay_attempts
        capability_scope_attempts += hardened.capability_scope_attempts

        denial_index = _first_denial_trace_index(comparison)
        if denial_index is not None:
            denial_indices.append(denial_index)

        cases.append(
            ChainCaseSummary(
                scenario_id=comparison.scenario.id,
                path=path.as_posix(),
                severity=comparison.scenario.severity,
                total_steps=hardened.total_steps,
                vulnerable_compromise=vulnerable.compromise,
                hardened_compromise=hardened.compromise,
                hardened_contained=hardened.contained,
                vulnerable_secret_leak=vulnerable.secret_leaked,
                hardened_secret_leak=hardened.secret_leaked,
                hardened_capability_denials=hardened.capability_denials,
                hardened_replay_attempts=hardened.capability_replay_attempts,
                hardened_scope_attempts=hardened.capability_scope_attempts,
                vulnerable_trace_valid=vulnerable.trace_valid,
                hardened_trace_valid=hardened.trace_valid,
                first_hardened_denial_trace_index=denial_index,
            )
        )

    mean_denial = (
        round(sum(denial_indices) / len(denial_indices), 2)
        if denial_indices
        else None
    )
    risk_reduction = (
        round((1.0 - (residual_risk / baseline_risk)) * 100.0, 2)
        if baseline_risk
        else 0.0
    )

    summary = ChainSuiteSummary(
        total_chains=len(paths),
        vulnerable_compromises=vulnerable_compromises,
        hardened_compromises=hardened_compromises,
        vulnerable_attack_success_rate=_rate(vulnerable_compromises, len(paths)),
        hardened_attack_success_rate=_rate(hardened_compromises, len(paths)),
        hardened_containment_rate=_rate(contained_attacks, vulnerable_attack_cases),
        trace_valid_rate=_rate(valid_traces, total_traces),
        capability_denials=capability_denials,
        capability_replay_attempts=capability_replay_attempts,
        capability_scope_attempts=capability_scope_attempts,
        mean_denial_trace_index=mean_denial,
        severity_weighted_baseline_risk=baseline_risk,
        severity_weighted_residual_risk=residual_risk,
        severity_weighted_risk_reduction=risk_reduction,
        cases=cases,
    )
    return ChainSuiteRun(summary=summary, comparisons=tuple(comparisons))


def _write_trace_jsonl(run: ChainSuiteRun, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for chain_path, comparison in run.comparisons:
            for result in (comparison.vulnerable, comparison.hardened):
                for event in result.trace:
                    record = {
                        "schema_version": "1.1",
                        "scenario_id": comparison.scenario.id,
                        "chain_path": chain_path.as_posix(),
                        "agent": result.agent,
                        "trace_valid": result.trace_valid,
                        "trace_head": result.trace_head,
                        "event": event.model_dump(mode="json"),
                    }
                    handle.write(
                        json.dumps(record, sort_keys=True, separators=(",", ":"))
                        + "\n"
                    )


def _render_html(summary: ChainSuiteSummary) -> str:
    rows = []
    for case in summary.cases:
        rows.append(
            "<tr>"
            f"<td>{html.escape(case.scenario_id)}</td>"
            f"<td>{html.escape(case.severity)}</td>"
            f"<td>{case.total_steps}</td>"
            f"<td>{'YES' if case.vulnerable_compromise else 'NO'}</td>"
            f"<td>{'YES' if case.hardened_compromise else 'NO'}</td>"
            f"<td>{'YES' if case.hardened_contained else 'NO'}</td>"
            f"<td>{case.hardened_capability_denials}</td>"
            f"<td>{case.first_hardened_denial_trace_index or '-'}</td>"
            f"<td>{'YES' if case.hardened_trace_valid else 'NO'}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Security Lab v1.1 Chain Benchmark</title>
<style>
body{{font-family:Inter,system-ui,-apple-system,sans-serif;margin:0;background:#0b1020;color:#e8edf7}}
main{{max-width:1200px;margin:auto;padding:32px}}
h1{{margin-bottom:6px}} .sub{{color:#9fb0cc;margin-bottom:24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:20px 0}}
.card{{background:#151d31;border:1px solid #26334f;border-radius:12px;padding:16px}}
.value{{font-size:28px;font-weight:700;margin-top:6px}}
table{{width:100%;border-collapse:collapse;background:#11182a}}
th,td{{padding:10px;border-bottom:1px solid #26334f;text-align:left;font-size:14px}}
th{{position:sticky;top:0;background:#18223a}}
.wrap{{overflow:auto;border:1px solid #26334f;border-radius:12px}}
.note{{margin-top:20px;color:#9fb0cc;font-size:13px;line-height:1.5}}
</style>
</head>
<body><main>
<h1>Agent Security Lab v1.1</h1>
<div class="sub">Deterministic stateful adversarial chain benchmark</div>
<div class="grid">
<div class="card">Attack chains<div class="value">{summary.total_chains}</div></div>
<div class="card">Vulnerable ASR<div class="value">{summary.vulnerable_attack_success_rate:.2f}%</div></div>
<div class="card">Hardened ASR<div class="value">{summary.hardened_attack_success_rate:.2f}%</div></div>
<div class="card">Containment<div class="value">{summary.hardened_containment_rate:.2f}%</div></div>
<div class="card">Valid traces<div class="value">{summary.trace_valid_rate:.2f}%</div></div>
<div class="card">Weighted risk reduction<div class="value">{summary.severity_weighted_risk_reduction:.2f}%</div></div>
</div>
<div class="wrap"><table>
<thead><tr><th>Scenario</th><th>Severity</th><th>Steps</th><th>Vuln compromise</th><th>Hard compromise</th><th>Contained</th><th>Cap denials</th><th>First denial event</th><th>Trace valid</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table></div>
<div class="note">
This benchmark uses deterministic local simulators and synthetic data. Trace integrity means the in-process SHA-256 hash chain verified successfully; it is not a claim of durable WORM storage, digital signatures, or universal production security.
</div>
</main></body></html>"""


def write_chain_suite_reports(
    run: ChainSuiteRun,
    reports_dir: Path,
) -> ChainSuiteReportPaths:
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_json = reports_dir / "chain-suite-summary.json"
    trace_jsonl = reports_dir / "chain-suite-traces.jsonl"
    html_report = reports_dir / "chain-suite-report.html"

    summary_json.write_text(
        run.summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    _write_trace_jsonl(run, trace_jsonl)
    html_report.write_text(_render_html(run.summary), encoding="utf-8")

    return ChainSuiteReportPaths(
        summary_json=summary_json,
        trace_jsonl=trace_jsonl,
        html_report=html_report,
    )
