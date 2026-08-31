# Threat Model - Agent Security Lab

## Security assumption

The language model is treated as potentially manipulated, confused, or hostile.

The lab evaluates whether external controls prevent an untrusted model proposal from becoming an unauthorized action.

## Protected assets

- tenant-scoped data
- canary secrets
- privileged tools
- approval-gated actions
- policy state
- execution authority

## Initial adversary capabilities

The adversary may provide malicious instructions, influence retrieved content, request unauthorized tools, request another tenant's resources, attempt to bypass human approval, or attempt sensitive-output disclosure.

## Initial trust boundaries

1. user/retrieved content -> model context
2. model proposal -> reference monitor
3. reference monitor -> tool execution
4. tenant selector -> tenant authority
5. approval request -> consequential action

## Non-goals for v0.1

- real credential harvesting
- exploitation of third-party services
- malware generation
- production penetration testing
- claims of universal prompt-injection prevention
