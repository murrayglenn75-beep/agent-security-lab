# Agent Security Lab

## 30-second overview

**Agent Security Lab is a defensive test bench for AI agents.** It deliberately puts vulnerable and hardened agent designs through the same hostile scenarios to show whether prompt injection, poisoned context, or manipulated model behavior can turn into unauthorized tool use or data exposure.

**What I built:** a deterministic red-team harness, external authorization/reference monitor, instrumented tool simulator, independent evaluator, security metrics, and JSON/HTML reporting.

**Why it matters:** the project tests a simple security principle — an AI model can be wrong or compromised without automatically gaining permission to cause real effects.


**Adversarial Security Evaluation for AI Agents**

Agent Security Lab (ASL) is a deterministic, reproducible red-team lab for testing whether an AI agent can turn hostile or manipulated model behavior into unauthorized effects.

It compares two reference designs:

- **Vulnerable agent:** untrusted model proposal → tool execution
- **Hardened agent:** untrusted model proposal → deterministic reference monitor → policy decision → tool execution or denial

The model is treated as potentially manipulated, confused, or hostile. Security decisions live outside the model.

## Current baseline

The v1.0 deterministic corpus contains **6 scenarios** covering:

- direct prompt injection
- indirect prompt injection
- secret exfiltration
- unauthorized tool use
- cross-tenant access
- human-approval bypass

The current local regression baseline intentionally produces a vulnerable-agent compromise in all 6 scenarios and 0 hardened-agent compromises. These numbers describe only the included deterministic corpus; they are **not** a universal security claim.

## Why this project exists

Prompt-injection resistance is not enough for agent security. A manipulated model should still be unable to gain authority it was never granted.

ASL therefore separates:

```text
Untrusted input
    ↓
Agent / model proposal
    ↓
Untrusted proposed action
    ↓
Reference monitor
    ↓
Tenant + policy + approval + tool checks
    ↓
Tool execution or denial
    ↓
Independent evaluator
    ↓
Metrics + JSON/HTML report
```

## Independent evaluation

The evaluator does not trust the agent's own `compromise`, `secret_leaked`, or authorization flags. It derives outcomes from:

- the tool execution audit log
- requested tenant boundaries
- protected canary values
- side-effect execution
- deterministic policy decisions

Regression tests also verify that the evaluator can both detect a compromise that an agent falsely claims is safe and clear a false compromise claim when no unsafe execution occurred.

## Quick start

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src
asl suite
```

Run one scenario:

```bash
asl run scenarios/direct_prompt_injection.yaml
```

Run the complete deterministic suite:

```bash
asl suite
```

Generated reports are written to `reports/` and are excluded from version control.

## Security metrics

ASL currently calculates:

- Attack Success Rate
- Secret Leakage Rate
- Unauthorized Tool Call Rate
- Cross-Tenant Violation Rate
- Human-Approval Bypass Rate

The suite produces both JSON and self-contained HTML reports.

## Repository structure

```text
src/agent_security_lab/
  agents.py          vulnerable and hardened reference agents
  evaluator.py       independent security outcome derivation
  metrics.py         deterministic security metrics
  policy.py          external reference monitor
  reporting.py       HTML benchmark reporting
  runner.py          isolated comparison runner
  scenario.py        YAML scenario loading
  suite.py           multi-scenario benchmark execution
  tools.py           instrumented local tool simulator
scenarios/           deterministic adversarial corpus
tests/               regression tests
docs/                threat model, methodology, taxonomy, validation
scripts/             public-release checks
```

## Security posture

ASL uses only local simulators and canary secrets. It is designed for defensive testing of intentionally vulnerable/hardened reference agents.

It does **not** provide malware, credential theft, real-world exploitation, or third-party attack automation.

See:

- `docs/THREAT_MODEL.md`
- `docs/METHODOLOGY.md`
- `docs/ATTACK_TAXONOMY.md`
- `docs/VALIDATION.md`
- `SECURITY.md`

## Roadmap

Planned extensions include:

- richer capability and tool-effect metadata
- multi-stage attack chains
- RAG poisoning simulator
- persistent memory poisoning simulator
- malicious tool-response / confused-deputy tests
- optional model-provider adapters
- larger benchmark corpus
- CI security-regression thresholds
- standards mapping to OWASP GenAI/Agentic guidance, NIST AI RMF, and MITRE ATLAS where applicable

## Limitations

The current v1.0 corpus is small and deterministic. A 0% hardened attack-success rate on these scenarios means the included regression controls held under those test conditions. It does not prove that the design is unbreakable, production-ready, or resistant to every prompt-injection or agentic attack.

## v1.1 Stateful Adversarial Evaluation

The v1.1 development branch adds multi-stage RAG and memory poisoning, scoped capability authorization, replay/expiry/subject/resource enforcement, SHA-256 hash-chained security traces, an independent security oracle, aggregate chain metrics, JSONL trace export, and CI security thresholds.

Run the full stateful benchmark:

```bash
asl chain-suite
```

The expanded repository contains 44 deterministic attack-chain cases plus the six v1.0 single-stage scenarios. These are synthetic regression cases, not a universal security guarantee.

See `docs/STATEFUL_ATTACK_CHAINS.md` and `docs/V1_1_VALIDATION.md`.
