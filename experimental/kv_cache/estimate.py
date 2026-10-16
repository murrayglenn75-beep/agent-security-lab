"""Analytical KV-cache budget estimator, not measured inference performance."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class KVConfig:
    layers: int
    kv_heads: int
    head_dim: int
    context_tokens: int
    concurrent_sequences: int = 1
    key_bytes: float = 2
    value_bytes: float = 2

def estimate_bytes(c: KVConfig) -> int:
    fields = (c.layers, c.kv_heads, c.head_dim, c.context_tokens, c.concurrent_sequences)
    if any(type(n) is not int or n <= 0 for n in fields):
        raise ValueError("integer dimensions must be positive")
    if any(type(n) not in (int, float) or not (0 < n <= 8) for n in (c.key_bytes, c.value_bytes)):
        raise ValueError("invalid K/V byte precision")
    return int(c.layers * c.kv_heads * c.head_dim * c.context_tokens
               * c.concurrent_sequences * (c.key_bytes + c.value_bytes))

def within_budget(c: KVConfig, *, cache_budget_bytes: int) -> bool:
    if type(cache_budget_bytes) is not int or cache_budget_bytes <= 0:
        raise ValueError("invalid cache budget")
    return estimate_bytes(c) <= cache_budget_bytes
