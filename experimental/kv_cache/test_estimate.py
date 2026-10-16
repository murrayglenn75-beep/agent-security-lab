from dataclasses import replace
import unittest

from experimental.kv_cache.estimate import KVConfig, estimate_bytes, within_budget

class CacheBudgetTests(unittest.TestCase):
    def setUp(self):
        self.config = KVConfig(layers=32, kv_heads=8, head_dim=128, context_tokens=4096)

    def test_exact_analytical_allocation(self):
        self.assertEqual(estimate_bytes(self.config), 536870912)

    def test_context_and_precision_scaling(self):
        self.assertEqual(estimate_bytes(replace(self.config, context_tokens=8192)),
                         2 * estimate_bytes(self.config))
        self.assertEqual(estimate_bytes(replace(self.config, key_bytes=1, value_bytes=1)),
                         estimate_bytes(self.config) // 2)

    def test_parallel_requests_increase_allocation(self):
        self.assertEqual(estimate_bytes(replace(self.config, concurrent_sequences=3)),
                         3 * estimate_bytes(self.config))

    def test_budget_fail_closed(self):
        self.assertFalse(within_budget(self.config, cache_budget_bytes=1000))
        self.assertTrue(within_budget(self.config, cache_budget_bytes=536870912))
        for invalid in (0, -1, True):
            with self.assertRaises(ValueError):
                within_budget(self.config, cache_budget_bytes=invalid)

    def test_invalid_architecture_rejected(self):
        for bad in (replace(self.config, layers=0), replace(self.config, kv_heads=True),
                    replace(self.config, key_bytes=-1)):
            with self.assertRaises(ValueError):
                estimate_bytes(bad)

if __name__ == "__main__":
    unittest.main()
