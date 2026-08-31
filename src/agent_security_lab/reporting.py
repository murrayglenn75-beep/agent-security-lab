from __future__ import annotations

from html import escape
from pathlib import Path

from .suite import SuiteResult


def _pct(value: float) -> str:
    return f"{value:.2f}%"


def render_suite_html(result: SuiteResult) -> str:
    """Render a self-contained, dependency-free HTML benchmark report."""
    rows = [
        ("Scenarios", str(result.scenario_count), str(result.scenario_count)),
        ("Compromises", str(result.vulnerable.compromises), str(result.hardened.compromises)),
        (
            "Attack success rate",
            _pct(result.vulnerable.attack_success_rate),
            _pct(result.hardened.attack_success_rate),
        ),
        (
            "Secret leakage rate",
            _pct(result.vulnerable.secret_leakage_rate),
            _pct(result.hardened.secret_leakage_rate),
        ),
        (
            "Unauthorized tool rate",
            _pct(result.vulnerable.unauthorized_tool_call_rate),
            _pct(result.hardened.unauthorized_tool_call_rate),
        ),
        (
            "Cross-tenant violation",
            _pct(result.vulnerable.cross_tenant_violation_rate),
            _pct(result.hardened.cross_tenant_violation_rate),
        ),
        (
            "Approval bypass rate",
            _pct(result.vulnerable.approval_bypass_rate),
            _pct(result.hardened.approval_bypass_rate),
        ),
    ]

    table_rows = "\n".join(
        "<tr>"
        f"<td>{escape(metric)}</td>"
        f"<td>{escape(vulnerable)}</td>"
        f"<td>{escape(hardened)}</td>"
        "</tr>"
        for metric, vulnerable, hardened in rows
    )

    scenario_rows = "\n".join(
        "<tr>"
        f"<td>{escape(v.scenario_id)}</td>"
        f"<td>{'YES' if v.compromise else 'NO'}</td>"
        f"<td>{'YES' if h.compromise else 'NO'}</td>"
        "</tr>"
        for v, h in zip(
            result.vulnerable_results,
            result.hardened_results,
            strict=True,
        )
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Security Lab Benchmark</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 980px; margin: 40px auto; padding: 0 20px; line-height: 1.5; }}
h1, h2 {{ line-height: 1.2; }}
table {{ width: 100%; border-collapse: collapse; margin: 18px 0 30px; }}
th, td {{ border: 1px solid #d0d7de; padding: 10px; text-align: left; }}
th {{ background: #f6f8fa; }}
.note {{ padding: 12px 14px; border: 1px solid #d0d7de; border-radius: 8px; background: #f6f8fa; }}
code {{ background: #f6f8fa; padding: 2px 5px; border-radius: 4px; }}
</style>
</head>
<body>
<h1>Agent Security Lab</h1>
<p>Deterministic adversarial security benchmark comparing an intentionally vulnerable agent with a hardened reference-monitor design.</p>
<div class="note">
<strong>Scope:</strong> This report covers {result.scenario_count} local deterministic scenarios. It is a regression baseline, not a claim of universal prompt-injection resistance or production security certification.
</div>
<h2>Security metrics</h2>
<table>
<thead><tr><th>Metric</th><th>Vulnerable</th><th>Hardened</th></tr></thead>
<tbody>{table_rows}</tbody>
</table>
<h2>Scenario outcomes</h2>
<table>
<thead><tr><th>Scenario</th><th>Vulnerable compromise</th><th>Hardened compromise</th></tr></thead>
<tbody>{scenario_rows}</tbody>
</table>
<h2>Evaluation model</h2>
<p>Security outcomes are derived by an independent evaluator from observed tool execution and protected-output leakage rather than trusted from the agent's own claims.</p>
</body>
</html>
"""


def write_html_report(result: SuiteResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_suite_html(result), encoding="utf-8")
    return path
