from __future__ import annotations

from .models import AgentResult, Scenario, TraceEvent
from .oracle import SecurityOracle
from .tools import ToolSimulator


def evaluate_result(
    scenario: Scenario,
    result: AgentResult,
    tools: ToolSimulator,
) -> AgentResult:
    """Derive security outcomes from observed tool execution, not agent self-report."""
    verdict = SecurityOracle().evaluate(scenario, [result.output], tools)

    trace = list(result.trace)
    next_step = max((event.step for event in trace), default=0) + 1
    trace.append(
        TraceEvent(
            step=next_step,
            event="independent_evaluator",
            detail=(
                f"executions={len(tools.execution_log)} "
                f"secret_leaked={verdict.secret_leaked} "
                f"unauthorized_tool={verdict.unauthorized_tool_call} "
                f"cross_tenant={verdict.cross_tenant_violation} "
                f"approval_bypass={verdict.approval_bypass}"
            ),
        )
    )

    return result.model_copy(
        update={
            "compromise": verdict.compromise,
            "secret_leaked": verdict.secret_leaked,
            "unauthorized_tool_call": verdict.unauthorized_tool_call,
            "cross_tenant_violation": verdict.cross_tenant_violation,
            "approval_bypass": verdict.approval_bypass,
            "trace": trace,
        }
    )
