# Agentic LLM evaluation exercises — Stanford CME 295 inspired

Source learning plan: CME 295 lectures 7 (RAG, tool calling, agents) and 8 (model evaluation, judges and benchmarks). No affiliation, endorsement or reuse of course material.

Local benchmark combines existing deterministic RAG metrics and adaptive context eligibility with labelled action/abstention fixtures. Explicit negative controls catch unsupported answers and unauthorized effects. All fixtures and labels are authored here, not held-out independently.

Run: `python -m unittest discover -s experimental/agent_eval -p 'test_*.py' -v` and `python -m experimental.agent_eval.benchmark`.

This benchmark is **not** an LLM, task-driven tool agent, independent grader, real production security test, or genuine SWE-bench/tau-bench evaluation. A perfect synthetic-fixture score does not demonstrate model intelligence or real-world tool safety.

Targets for independent adoption: AAK policy/effect trace; TANDEM real tool-driven task sequence; APEX Windows local model completion and exact token/RAM metrics; FORGE crash/restart journal verification. All require authentic connected sources and separate external validation.
