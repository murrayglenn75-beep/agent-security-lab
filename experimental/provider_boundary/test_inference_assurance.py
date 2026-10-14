import unittest

from inference_assurance import Capacity, benchmark_report, preflight, readiness


class InferenceAssuranceTests(unittest.TestCase):
    def test_context_capacity(self):
        self.assertTrue(preflight(60, 32, Capacity(100, 40)))

    def test_context_overrun(self):
        with self.assertRaises(ValueError):
            preflight(80, 32, Capacity(100, 40))

    def test_output_limit(self):
        with self.assertRaises(ValueError):
            preflight(20, 50, Capacity(100, 40))

    def test_negative_tokens(self):
        with self.assertRaises(ValueError):
            preflight(-1, 5, Capacity(100, 40))

    def test_bool_tokens_rejected(self):
        with self.assertRaises(ValueError):
            preflight(True, 5, Capacity(100, 40))

    def test_readiness_requires_generation(self):
        self.assertFalse(readiness(lambda: "OK"))
        self.assertTrue(readiness(lambda: "READY"))

    def test_readiness_fail_closed(self):
        def broken():
            raise TimeoutError("cold start")

        self.assertFalse(readiness(broken))

    def test_cost_per_success(self):
        report = benchmark_report([10, 20, 30, 40], successful_tasks=2,
                                  total_cost_usd=4, idle_cost_usd=1,
                                  attempts=4, cache_hits=3)
        self.assertEqual(report["cost_per_successful_task_usd"], 2)
        self.assertEqual(report["failure_count"], 2)
        self.assertEqual(report["cache_hit_fraction"], 0.75)
        self.assertEqual(report["p95_ms"], 40)

    def test_no_success_not_zero_cost(self):
        self.assertIsNone(benchmark_report([1], total_cost_usd=5)[
            "cost_per_successful_task_usd"])

    def test_invalid_cost(self):
        with self.assertRaises(ValueError):
            benchmark_report([1], total_cost_usd=2, idle_cost_usd=3)

    def test_invalid_samples(self):
        with self.assertRaises(ValueError):
            benchmark_report([float("nan")])

    def test_invalid_cache(self):
        with self.assertRaises(ValueError):
            benchmark_report([1], attempts=1, cache_hits=2)


if __name__ == "__main__":
    unittest.main()
