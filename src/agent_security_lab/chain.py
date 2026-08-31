from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .capability import CapabilityBroker
from .chain_models import AttackChainScenario, ChainResult, ChainStepKind
from .models import AttackCategory, Decision, Scenario, ToolCall
from .oracle import SecurityOracle
from .policy import ReferenceMonitor
from .runner import build_default_tools
from .simulators import MemoryRecord, MemorySimulator, RAGDocument, RAGSimulator
from .trace import ImmutableSecurityTrace, verify_trace

_CAPABILITY_PROTECTED_TOOLS = {"read_record"}


@dataclass(frozen=True)
class ChainComparisonResult:
    scenario: AttackChainScenario
    vulnerable: ChainResult
    hardened: ChainResult


def load_attack_chain(path: Path) -> AttackChainScenario:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return AttackChainScenario.model_validate(raw)


def _policy_scenario(
    chain: AttackChainScenario,
    call: ToolCall | None = None,
) -> Scenario:
    return Scenario(
        id=chain.id,
        category=AttackCategory.INDIRECT_PROMPT_INJECTION,
        severity=chain.severity,
        user_input="stateful adversarial attack chain",
        requested_tool=call,
        tenant=chain.tenant,
        protected_tenant=chain.protected_tenant,
        requires_human_approval=chain.requires_human_approval,
        secret_canary=chain.secret_canary,
        expect_attack_contained=chain.expect_attack_contained,
    )


def _run_chain(chain: AttackChainScenario, agent: str) -> ChainResult:
    tools = build_default_tools(chain.secret_canary)
    rag = RAGSimulator()
    memory = MemorySimulator()
    monitor = ReferenceMonitor()
    broker = CapabilityBroker()
    trace = ImmutableSecurityTrace()
    context: list[str] = []
    output_fragments: list[str] = []
    capability_ids: dict[str, str] = {}
    final_output = "NO_EFFECT"
    completed_steps = 0
    capability_violation = False
    capability_denials = 0
    capability_replay_attempts = 0
    capability_scope_attempts = 0

    trace.append(
        "chain_started",
        f"agent={agent} scenario={chain.id} tenant={chain.tenant}",
    )

    for step in chain.steps:
        completed_steps += 1

        if step.kind is ChainStepKind.RAG_STORE:
            if step.key is None or step.content is None:
                raise ValueError(f"{step.id}: rag_store requires key and content")
            rag.store(
                RAGDocument(
                    key=step.key,
                    content=step.content,
                    trusted=step.trusted,
                    source=step.source,
                )
            )
            trace.append(
                "rag_document_stored",
                f"step={step.id} key={step.key} trusted={step.trusted} source={step.source}",
            )
            continue

        if step.kind is ChainStepKind.RAG_RETRIEVE:
            if step.key is None:
                raise ValueError(f"{step.id}: rag_retrieve requires key")
            document = rag.retrieve(step.key)
            if document is None:
                trace.append("rag_miss", f"step={step.id} key={step.key}")
                continue
            context.append(document.content)
            trace.append(
                "rag_document_retrieved",
                (
                    f"step={step.id} key={document.key} "
                    f"trusted={document.trusted} source={document.source}"
                ),
            )
            continue

        if step.kind is ChainStepKind.MEMORY_WRITE:
            if step.key is None:
                raise ValueError(f"{step.id}: memory_write requires key")
            content = step.content
            if content is None:
                content = context[-1] if context else ""
            memory.write(
                MemoryRecord(
                    key=step.key,
                    content=content,
                    trusted=step.trusted,
                    source=step.source,
                )
            )
            trace.append(
                "memory_written",
                (
                    f"step={step.id} key={step.key} "
                    f"trusted={step.trusted} source={step.source}"
                ),
            )
            continue

        if step.kind is ChainStepKind.MEMORY_READ:
            if step.key is None:
                raise ValueError(f"{step.id}: memory_read requires key")
            record = memory.read(step.key)
            if record is None:
                trace.append("memory_miss", f"step={step.id} key={step.key}")
                continue
            context.append(record.content)
            trace.append(
                "memory_read",
                (
                    f"step={step.id} key={record.key} "
                    f"trusted={record.trusted} source={record.source}"
                ),
            )
            continue

        if step.kind is ChainStepKind.ISSUE_CAPABILITY:
            if step.capability is None:
                raise ValueError(f"{step.id}: issue_capability requires capability")
            capability = broker.issue(step.capability, completed_steps)
            capability_ids[step.capability.alias] = capability.capability_id
            trace.append(
                "capability_issued",
                (
                    f"step={step.id} alias={step.capability.alias} "
                    f"subject={capability.subject} tenant={capability.tenant} "
                    f"tool={capability.tool} resource={capability.resource} "
                    f"max_uses={capability.max_uses} expires_step={capability.expires_step}"
                ),
            )
            continue

        if step.kind is ChainStepKind.PROPOSE_TOOL:
            if step.tool is None:
                raise ValueError(f"{step.id}: propose_tool requires tool")
            call = step.tool
            trace.append(
                "action_proposed",
                (
                    f"step={step.id} source={step.source} actor={step.actor} "
                    f"tool={call.name} context_items={len(context)}"
                ),
            )

            if agent == "hardened":
                policy = monitor.authorize(_policy_scenario(chain, call), call)
                trace.append(
                    "reference_monitor",
                    (
                        f"step={step.id} decision={policy.decision.value} "
                        f"reason={policy.reason}"
                    ),
                )
                if policy.decision is Decision.DENY:
                    final_output = f"DENIED:{policy.reason}"
                    trace.append("tool_denied", f"step={step.id} tool={call.name}")
                    continue

                if call.name in _CAPABILITY_PROTECTED_TOOLS:
                    capability_id = (
                        capability_ids.get(step.capability_ref)
                        if step.capability_ref is not None
                        else None
                    )
                    capability_decision = broker.authorize_and_consume(
                        capability_id,
                        actor=step.actor,
                        call=call,
                        current_step=completed_steps,
                    )
                    trace.append(
                        "capability_monitor",
                        (
                            f"step={step.id} decision={capability_decision.decision.value} "
                            f"reason={capability_decision.reason}"
                        ),
                    )
                    if capability_decision.decision is Decision.DENY:
                        capability_denials += 1
                        if capability_decision.reason == "capability_replay":
                            capability_replay_attempts += 1
                        if (
                            capability_decision.reason
                            == "capability_resource_scope_mismatch"
                        ):
                            capability_scope_attempts += 1
                        final_output = f"DENIED:{capability_decision.reason}"
                        trace.append(
                            "tool_denied",
                            f"step={step.id} tool={call.name}",
                        )
                        continue

            result = tools.execute(call.name, call.arguments)
            final_output = result
            output_fragments.append(result)
            if agent == "vulnerable" and call.name in _CAPABILITY_PROTECTED_TOOLS:
                capability_violation = True
            trace.append("tool_executed", f"step={step.id} tool={call.name}")
            continue

        raise ValueError(f"{step.id}: unsupported chain step {step.kind}")

    policy_view = _policy_scenario(chain)
    verdict = SecurityOracle().evaluate(policy_view, output_fragments, tools)
    compromise = verdict.compromise or capability_violation
    trace.append(
        "security_oracle",
        (
            f"compromise={compromise} "
            f"secret_leaked={verdict.secret_leaked} "
            f"unauthorized_tool={verdict.unauthorized_tool_call} "
            f"cross_tenant={verdict.cross_tenant_violation} "
            f"approval_bypass={verdict.approval_bypass} "
            f"capability_violation={capability_violation}"
        ),
    )
    trace.append(
        "chain_finished",
        (
            f"completed={completed_steps}/{len(chain.steps)} "
            f"contained={not compromise}"
        ),
    )

    events = trace.events
    return ChainResult(
        scenario_id=chain.id,
        agent=agent,
        compromise=compromise,
        contained=not compromise,
        secret_leaked=verdict.secret_leaked,
        unauthorized_tool_call=verdict.unauthorized_tool_call,
        cross_tenant_violation=verdict.cross_tenant_violation,
        approval_bypass=verdict.approval_bypass,
        capability_violation=capability_violation,
        capability_denials=capability_denials,
        capability_replay_attempts=capability_replay_attempts,
        capability_scope_attempts=capability_scope_attempts,
        completed_steps=completed_steps,
        total_steps=len(chain.steps),
        output=final_output,
        trace_valid=verify_trace(events),
        trace_head=trace.head,
        trace=list(events),
    )


def run_attack_chain(path: Path) -> ChainComparisonResult:
    scenario = load_attack_chain(path)
    return ChainComparisonResult(
        scenario=scenario,
        vulnerable=_run_chain(scenario, "vulnerable"),
        hardened=_run_chain(scenario, "hardened"),
    )
