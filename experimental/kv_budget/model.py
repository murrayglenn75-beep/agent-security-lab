"""Analytical KV-cache capacity model; not an actual inference benchmark."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KVConfiguration:
    layers: int
    kv_heads: int
    head_dim: int
    context_tokens: int
    key_bytes: float
    value_bytes: float
    concurrent_sequences: int = 1


def estimate_bytes(c: KVConfiguration) -> int:
    if any(type(v) is not int or v <= 0 for v in (
        c.layers, c.kv_heads, c.head_dim, c.context_tokens, c.concurrent_sequences
    )):
        raise ValueError("positive integer shape required")
    if any(type(v) not in (int, float) or v <= 0 or v != v or v == float("inf")
           for v in (c.key_bytes, c.value_bytes)):
        raise ValueError("finite positive KV precision required")
    return int(c.layers * c.kv_heads * c.head_dim * c.context_tokens
               * (c.key_bytes + c.value_bytes) * c.concurrent_sequences)


def budget(c: KVConfiguration, *, ram_limit_bytes: int, reserved_bytes: int) -> dict:
    if (type(ram_limit_bytes) is not int or type(reserved_bytes) is not int
            or reserved_bytes < 0 or ram_limit_bytes <= reserved_bytes):
        raise ValueError("invalid RAM allowance")
    estimate = estimate_bytes(c)
    return {
        "estimated_kv_bytes": estimate,
        "available_kv_bytes": ram_limit_bytes - reserved_bytes,
        "within_analytical_budget": estimate <= ram_limit_bytes - reserved_bytes,
        "scope": "analytical_only_not_measured",
    }
