"""Opt-in local/cloud OpenAI-compatible HTTP inference adapters.

No tools, streaming, environment credential discovery, or automatic retries.
"""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request as HttpRequest
from urllib.parse import urlsplit
from urllib.request import urlopen

from provider_boundary import Provider, ProviderError, Response


def openai_compatible(name, endpoint, model, max_tokens, data_classes,
                      api_key=None, usd_per_million_input=0.0,
                      usd_per_million_output=0.0, local=False):
    url = urlsplit(endpoint)
    if url.username or url.password or url.fragment or url.query:
        raise ValueError("endpoint cannot embed credentials or query")
    if local:
        if url.scheme != "http" or url.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("local adapter must use loopback")
        if api_key:
            raise ValueError("local adapter does not accept a cloud key")
    elif url.scheme != "https" or not api_key:
        raise ValueError("cloud adapter requires HTTPS and explicit API key")
    if not endpoint.endswith("/chat/completions"):
        raise ValueError("expected explicit chat/completions endpoint")
    if any(not isinstance(v, (int, float)) or v < 0 for v in
           (usd_per_million_input, usd_per_million_output)):
        raise ValueError("invalid price configuration")

    def call(request):
        payload = json.dumps({
            "model": model, "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens, "stream": False
        }).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key is not None:
            headers["Authorization"] = "Bearer " + api_key
        try:
            response = urlopen(
                HttpRequest(endpoint, data=payload, headers=headers, method="POST"),
                timeout=request.timeout_ms / 1000,
            )
            with response:
                if response.status != 200:
                    raise ProviderError("HTTP_UNEXPECTED_STATUS")
                raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ProviderError("RESPONSE_TOO_LARGE")
            data = json.loads(raw)
            content = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            input_tokens = usage["prompt_tokens"]
            output_tokens = usage["completion_tokens"]
            if not isinstance(content, str) or any(
                not isinstance(x, int) or isinstance(x, bool) or x < 0
                for x in (input_tokens, output_tokens)
            ):
                raise ValueError("invalid response body")
            cost = (input_tokens * usd_per_million_input +
                    output_tokens * usd_per_million_output) / 1_000_000
            return Response(content, name, model, input_tokens, output_tokens, cost)
        except HTTPError as error:
            # Never treat uncertain transport outcomes as safely retryable.
            raise ProviderError("HTTP_" + str(error.code), retryable=False) from None
        except (URLError, TimeoutError) as error:
            raise ProviderError("TRANSPORT_UNCERTAIN", retryable=False) from error
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ProviderError("INVALID_PROVIDER_RESPONSE", retryable=False) from error

    return Provider(name, call, frozenset({model}), frozenset(data_classes), max_tokens)
