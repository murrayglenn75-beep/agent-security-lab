# Stateful Adversarial Evaluation Architecture

```text
Attack Corpus / Scenario DSL
            |
            v
Attack-Chain Orchestrator
            |
            v
RAG Simulator --- Memory Simulator
            |
            v
Vulnerable Agent / Hardened Agent
            |
            v
Proposed Tool Action
            |
            v
General Policy Reference Monitor
            |
            v
Scoped Capability Monitor
            |
            v
Instrumented Tool Runtime
            |
            v
SHA-256 Hash-Chained Security Trace
            |
            v
Independent Security Oracle
            |
            v
Metrics / Risk Scoring / JSON / JSONL / HTML / CI
```

## Authority model

The model is not the authority source. Tool proposals are untrusted inputs to deterministic enforcement.

A capability can be bound to:

- a subject;
- a tenant;
- a tool;
- a resource;
- a maximum use count;
- a deterministic expiry step;
- an approval state.

Capability IDs in the local benchmark are deterministic synthetic identifiers for reproducible testing. They are not production bearer-token cryptography.

## Stateful attack families

The v1.1 corpus includes retrieval poisoning, memory poisoning, persistence from retrieval into memory, capability resource-scope escalation, capability theft, replay, expiry, unapproved capability use, tool-scope mismatch, and tenant-scope mismatch.

The vulnerable and hardened paths are run in isolated tool environments to avoid cross-test contamination.
