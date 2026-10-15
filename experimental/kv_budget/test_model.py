import unittest
from dataclasses import replace

from experimental.kv_budget.model import KVConfiguration, budget, estimate_bytes

CONFIG = KVConfiguration(32, 8, 128, 4096, 2, 2)


class KVTests(unittest.TestCase):
    def test_linear_with_context_and_sessions(self):
        self.assertEqual(estimate_bytes(replace(CONFIG, context_tokens=8192)),
                         2 * estimate_bytes(CONFIG))
        self.assertEqual(estimate_bytes(replace(CONFIG, concurrent_sequences=2)),
                         2 * estimate_bytes(CONFIG))

    def test_kv_quantization_reduces_estimate(self):
        compact = replace(CONFIG, key_bytes=1, value_bytes=1)
        self.assertEqual(estimate_bytes(compact) * 2, estimate_bytes(CONFIG))

    def test_memory_reservation_can_fail_closed(self):
        self.assertFalse(budget(CONFIG, ram_limit_bytes=16 * 1024**3,
                                reserved_bytes=16 * 1024**3 - 1024)["within_analytical_budget"])

    def test_invalid_shape_denied(self):
        with self.assertRaises(ValueError):
            estimate_bytes(replace(CONFIG, kv_heads=0))
        with self.assertRaises(ValueError):
            budget(CONFIG, ram_limit_bytes=1024, reserved_bytes=1024)


if __name__ == "__main__":
    unittest.main()
