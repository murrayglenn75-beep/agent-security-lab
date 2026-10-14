# LiteLLM-inspired inference gateway contract — experimental

No LiteLLM dependency, API keys, or network calls. This is a pure Python interface prototype and fake-provider test suite.

Application code can use a stable request/response envelope; adapters encapsulate provider differences. The gateway checks an explicit allowed-provider policy, data classification, model capability and a result cost ceiling. Only inference-only operations are accepted. Errors may enable one-way fallback **only for explicitly opted-in, side-effect-free inference requests**. There is no general retry of tools or payments.

Caveats: Provider billing cannot be enforced after a completed expensive request by simply inspecting response usage. A production gateway needs *pre-call quota reservation*, max-token cost estimates, authenticated credentials outside the model process, rate limiting, streaming cancellation, bounded timeouts, transport error normalization, and an independent AAK authorization service. Fake-adapter tests do not demonstrate vendor API compatibility, reliability, or real cost enforcement. Use this contract only as a reference for APEX/FORGE/TANDEM integration.
