"""Side-effect-free, provider-neutral inference contract prototype. No network calls."""
from collections.abc import Callable
from dataclasses import dataclass


class ProviderError(Exception):
    def __init__(self, code, retryable=False):
        self.code=code
        self.retryable=retryable
        super().__init__(code)

@dataclass(frozen=True)
class Request:
    request_id: str
    prompt: str
    model: str
    max_tokens: int
    timeout_ms: int
    max_cost_usd: float
    data_class: str = "public"
    allow_fallback: bool = False
    effect_class: str = "inference_only"

@dataclass(frozen=True)
class Response:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

@dataclass(frozen=True)
class Provider:
    name: str
    invoke: Callable
    models: frozenset
    allowed_data_classes: frozenset
    max_tokens: int

def invoke(request, providers, policy):
    if not isinstance(request, Request) or request.effect_class!="inference_only":
        raise ValueError("effects cannot cross the model-inference gateway")
    if not request.request_id or not request.prompt or request.max_tokens<1 or request.timeout_ms<1 or request.max_cost_usd<0:
        raise ValueError("invalid request")
    if not isinstance(providers,(tuple,list)) or not providers:
        raise ValueError("missing provider")
    if not isinstance(policy,dict) or policy.get("allowed_providers") is None:
        raise ValueError("missing explicit policy")
    attempts=[]
    for i,provider in enumerate(providers):
        if i>0 and not request.allow_fallback: break
        if provider.name not in policy["allowed_providers"]: continue
        if request.data_class not in provider.allowed_data_classes: continue
        if request.model not in provider.models or request.max_tokens>provider.max_tokens: continue
        try:
            result=provider.invoke(request)
        except ProviderError as error:
            attempts.append({"provider":provider.name,"failure_code":error.code})
            if not error.retryable: break
            continue
        if not isinstance(result,Response) or result.provider!=provider.name or result.model!=request.model:
            raise ValueError("invalid provider result")
        if min(result.input_tokens,result.output_tokens)<0 or not (0<=result.cost_usd<=request.max_cost_usd):
            raise ValueError("invalid usage or exceeded cost ceiling")
        return result,attempts
    raise ProviderError("NO_AUTHORIZED_PROVIDER_OR_SAFE_RESULT")
