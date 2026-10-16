"""Conservative architectural KV-cache estimate and RAM budget check."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CacheShape:
    layers: int
    kv_heads: int
    head_dim: int
    tokens: int
    key_bytes: float
    value_bytes: float

def kv_bytes(shape: CacheShape) -> int:
    vals=(shape.layers,shape.kv_heads,shape.head_dim,shape.tokens)
    if any(type(v) is not int or v<=0 for v in vals):
        raise ValueError("positive integer dimensions required")
    if any(type(v) not in (int,float) or not 0<v<=8 for v in (shape.key_bytes,shape.value_bytes)):
        raise ValueError("invalid element sizes")
    if shape.tokens>10_000_000:
        raise ValueError("unsupported context")
    return int(shape.layers*shape.kv_heads*shape.head_dim*shape.tokens*(shape.key_bytes+shape.value_bytes))

def budget(shape: CacheShape, *, model_bytes: int, overhead_bytes: int, ram_bytes: int)->dict:
    if any(type(v) is not int or v<0 for v in (model_bytes,overhead_bytes,ram_bytes)) or ram_bytes==0:
        raise ValueError("invalid capacity")
    kv=kv_bytes(shape)
    total=model_bytes+overhead_bytes+kv
    return {"kv_bytes":kv,"estimated_total_bytes":total,"fits_estimate":total<=ram_bytes,
            "note":"Architectural estimate only; allocation and measured peak RSS differ."}
