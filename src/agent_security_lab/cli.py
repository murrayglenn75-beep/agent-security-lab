from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .reporting import write_html_report
from .runner import run_comparison
from .scenario import load_scenario
from .suite import run_suite

app = typer.Typer(
    help="Agent Security Lab CLI",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main() -> None:
    """Adversarial security evaluation for AI agents."""


@app.command()
def run(path: Path) -> None:
    """Run one scenario against vulnerable and hardened agents."""
    scenario = load_scenario(path)
    comparison = run_comparison(scenario)

    table = Table(title=f"Agent Security Lab - {scenario.id}")
    table.add_column("Agent")
    table.add_column("Decision")
    table.add_column("Compromise")
    table.add_column("Secret leak")
    table.add_column("Cross-tenant")
    table.add_column("Approval bypass")

    for result in (comparison.vulnerable, comparison.hardened):
        table.add_row(
            result.agent, result.decision.value, str(result.compromise),
            str(result.secret_leaked), str(result.cross_tenant_violation),
            str(result.approval_bypass),
        )

    console.print(table)
    console.print("\nHardened trace")
    for event in comparison.hardened.trace:
        console.print(f"[{event.step:02}] {event.event}: {event.detail}")

    payload = {
        "scenario": scenario.model_dump(mode="json"),
        "vulnerable": comparison.vulnerable.model_dump(mode="json"),
        "hardened": comparison.hardened.model_dump(mode="json"),
    }
    report_path = Path("reports") / f"{scenario.id}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print(f"\nReport: {report_path}")


@app.command()
def suite(directory: Path = Path("scenarios")) -> None:
    """Run every YAML scenario and print comparable security metrics."""
    result = run_suite(directory)

    table = Table(title="Agent Security Lab - Suite Benchmark")
    table.add_column("Metric")
    table.add_column("Vulnerable", justify="right")
    table.add_column("Hardened", justify="right")

    rows = [
        ("Scenarios", result.scenario_count, result.scenario_count),
        ("Compromises", result.vulnerable.compromises, result.hardened.compromises),
        (
            "Attack success rate",
            f"{result.vulnerable.attack_success_rate:.2f}%",
            f"{result.hardened.attack_success_rate:.2f}%",
        ),
        (
            "Secret leakage rate",
            f"{result.vulnerable.secret_leakage_rate:.2f}%",
            f"{result.hardened.secret_leakage_rate:.2f}%",
        ),
        (
            "Unauthorized tool rate",
            f"{result.vulnerable.unauthorized_tool_call_rate:.2f}%",
            f"{result.hardened.unauthorized_tool_call_rate:.2f}%",
        ),
        (
            "Cross-tenant violation",
            f"{result.vulnerable.cross_tenant_violation_rate:.2f}%",
            f"{result.hardened.cross_tenant_violation_rate:.2f}%",
        ),
        (
            "Approval bypass rate",
            f"{result.vulnerable.approval_bypass_rate:.2f}%",
            f"{result.hardened.approval_bypass_rate:.2f}%",
        ),
    ]

    for metric, vulnerable, hardened in rows:
        table.add_row(metric, str(vulnerable), str(hardened))

    console.print(table)

    report_path = Path("reports") / "suite-summary.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    html_path = write_html_report(result, Path("reports") / "suite-summary.html")
    console.print(f"\nSuite report: {report_path}")
    console.print(f"Suite HTML: {html_path}")


if __name__ == "__main__":
    app()
