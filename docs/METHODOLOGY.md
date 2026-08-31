# Evaluation Methodology

## Goal

Agent Security Lab asks a narrow question:

> If the model-facing portion of an agent becomes manipulated or hostile, can that state cross an authority boundary and cause a protected effect?

The lab is designed around containment rather than a claim that prompt injection can always be prevented.

## Comparison design

Each scenario is executed twice:

1. against an intentionally vulnerable agent;
2. against a hardened agent using an external deterministic reference monitor.

Each run receives an isolated tool environment so one run cannot contaminate the other.

## Trust boundaries

Model output is an **untrusted proposal**. Authorization is performed outside the model.

The current reference monitor evaluates:

- tenant boundary
- approval requirement
- forbidden external side effects
- secret-access authorization

## Independent evaluator

The evaluator derives security outcomes from observed execution instead of trusting agent-reported labels.

Evidence includes:

- recorded tool calls
- tool arguments
- tenant requested by the execution
- protected canaries present in output
- whether an approval-gated action executed

This prevents a compromised agent from declaring itself safe.

## Determinism

v1.0 requires no API key or external model. The baseline is intentionally deterministic so security regressions can be reproduced in CI.

## Interpretation

A hardened ASR of 0% means **none of the included deterministic scenarios compromised the hardened reference design**.

It must not be interpreted as:

- universal prompt-injection immunity
- formal verification
- penetration-test certification
- production-readiness evidence
- a guarantee against unknown attack classes
