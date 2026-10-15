"""Dependency-free educational rotary position embedding reference; not inference code."""
from __future__ import annotations

import math


def rotate(vector: tuple[float, ...], position: int, *, theta: float = 10000.0) -> tuple[float, ...]:
    if not vector or len(vector) % 2 or type(position) is not int or position < 0:
        raise ValueError("even-length vector and nonnegative integer position required")
    if not math.isfinite(theta) or theta <= 1:
        raise ValueError("invalid rotary base")
    if any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in vector):
        raise ValueError("finite numeric vector required")
    half = len(vector) // 2
    result = []
    for i in range(half):
        angle = position / (theta ** (2 * i / len(vector)))
        a, b = vector[2 * i], vector[2 * i + 1]
        result.extend((a * math.cos(angle) - b * math.sin(angle),
                       a * math.sin(angle) + b * math.cos(angle)))
    return tuple(result)


def dot(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b):
        raise ValueError("mismatched vectors")
    return sum(x * y for x, y in zip(a, b))
