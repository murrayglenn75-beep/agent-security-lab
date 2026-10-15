import unittest

from experimental.trace_contract.trace import Span, validate_dict, validate_trace


class TraceContractTests(unittest.TestCase):
    def test_valid_nested_trace(self):
        spans = [Span("trace1", "root", None, "tool", 0, 100, "ok"),
                 Span("trace1", "retrieval", "root", "retrieval", 20, 80, "ok", input_tokens=20)]
        validate_trace(spans)

    def test_rejects_raw_prompt_and_secret_keys(self):
        base = {"trace_id": "t", "span_id": "s", "parent_id": None, "stage": "generation",
                "start_ms": 0, "end_ms": 10, "outcome": "ok"}
        with self.assertRaises(ValueError):
            validate_dict({**base, "raw_prompt": "private"})
        with self.assertRaises(ValueError):
            validate_dict({**base, "api_key": "secret"})

    def test_unknown_and_negative_cost(self):
        base = {"trace_id": "t", "span_id": "s", "parent_id": None, "stage": "generation",
                "start_ms": 0, "end_ms": 10, "outcome": "ok"}
        with self.assertRaises(ValueError):
            validate_dict({**base, "estimated_cost_usd": -1.0})
        with self.assertRaises(ValueError):
            validate_dict({**base, "extra": "anything"})

    def test_wrong_parent_and_duplicate(self):
        root = Span("t", "a", None, "tool", 0, 5, "ok")
        child = Span("t", "b", "a", "retrieval", 1, 10, "ok")
        with self.assertRaises(ValueError):
            validate_trace([root, child])
        with self.assertRaises(ValueError):
            validate_trace([root, root])

    def test_estimate_and_billed_cost_distinct(self):
        s = validate_dict({"trace_id": "t", "span_id": "s", "parent_id": None,
                           "stage": "generation", "start_ms": 0, "end_ms": 4, "outcome": "ok",
                           "estimated_cost_usd": 0.1})
        self.assertIsNone(s.billed_cost_usd)


if __name__ == "__main__":
    unittest.main()
