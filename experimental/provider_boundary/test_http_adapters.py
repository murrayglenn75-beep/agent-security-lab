import io
import json
import unittest
from unittest.mock import patch

from http_adapters import openai_compatible
from provider_boundary import ProviderError, Request, invoke


class StubResponse:
    status = 200

    def __init__(self, payload):
        self.buffer = io.BytesIO(json.dumps(payload).encode())

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self, n):
        return self.buffer.read(n)


def request(**changes):
    data = {"request_id": "r", "prompt": "hello", "model": "test-model", "max_tokens": 32,
            "timeout_ms": 1000, "max_cost_usd": 0.1}
    data.update(changes)
    return Request(**data)


class AdapterTests(unittest.TestCase):
    def local(self):
        return openai_compatible("local", "http://127.0.0.1:8080/v1/chat/completions",
                                 "test-model", 64, {"public"}, local=True)

    def cloud(self):
        return openai_compatible("cloud", "https://example.com/v1/chat/completions",
                                 "test-model", 64, {"public"}, api_key="fixture-key",
                                 usd_per_million_input=1.0, usd_per_million_output=2.0)

    @patch("http_adapters.urlopen")
    def test_local_round_trip(self, mock):
        mock.return_value = StubResponse({"choices": [{"message": {"content": "ok"}}],
                                          "usage": {"prompt_tokens": 4, "completion_tokens": 2}})
        response, _ = invoke(request(), [self.local()], {"allowed_providers": {"local"}})
        self.assertEqual(response.text, "ok")
        body = json.loads(mock.call_args.args[0].data)
        self.assertFalse(body["stream"])
        self.assertNotIn("tools", body)

    @patch("http_adapters.urlopen")
    def test_cloud_cost(self, mock):
        mock.return_value = StubResponse({"choices": [{"message": {"content": "ok"}}],
                                          "usage": {"prompt_tokens": 3, "completion_tokens": 5}})
        response, _ = invoke(request(), [self.cloud()], {"allowed_providers": {"cloud"}})
        self.assertEqual(response.cost_usd, 0.000013)

    def test_local_rejects_remote(self):
        with self.assertRaises(ValueError):
            openai_compatible("local", "http://evil.example/v1/chat/completions",
                              "test-model", 32, {"public"}, local=True)

    def test_cloud_rejects_plaintext(self):
        with self.assertRaises(ValueError):
            openai_compatible("cloud", "http://example.com/v1/chat/completions",
                              "test-model", 32, {"public"}, api_key="x")

    @patch("http_adapters.urlopen")
    def test_invalid_response_no_fallback(self, mock):
        mock.return_value = StubResponse({"choices": []})
        with self.assertRaises(ProviderError):
            invoke(request(allow_fallback=True), [self.local(), self.cloud()],
                   {"allowed_providers": {"cloud", "local"}})
        self.assertEqual(mock.call_count, 1)

    @patch("http_adapters.urlopen")
    def test_cost_ceiling_is_checked(self, mock):
        mock.return_value = StubResponse({"choices": [{"message": {"content": "ok"}}],
                                          "usage": {"prompt_tokens": 1000000, "completion_tokens": 5}})
        with self.assertRaises(ValueError):
            invoke(request(), [self.cloud()], {"allowed_providers": {"cloud"}})

    def test_cloud_secrets_not_from_environment(self):
        with self.assertRaises(ValueError):
            openai_compatible("cloud", "https://example.com/v1/chat/completions",
                              "test-model", 32, {"public"})

    def test_private_not_routed_to_public_adapter(self):
        with self.assertRaises(ProviderError):
            invoke(request(data_class="confidential"), [self.local()],
                   {"allowed_providers": {"local"}})


if __name__ == "__main__":
    unittest.main()
