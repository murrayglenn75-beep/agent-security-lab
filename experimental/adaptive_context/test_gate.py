import unittest
from dataclasses import replace

from experimental.adaptive_context.gate import ContextRequest, choose

BASE = ContextRequest("w", "w", True, True, 200, 1000, 3, False, False, True)

class ContextGateTests(unittest.TestCase):
    def test_small_stable_context(self):
        self.assertEqual(choose(BASE).strategy, "cag")

    def test_large_or_changing_context(self):
        self.assertEqual(choose(replace(BASE, corpus_tokens=1001)).strategy, "rag")
        self.assertEqual(choose(replace(BASE, changing=True)).strategy, "rag")
        self.assertEqual(choose(replace(BASE, requires_current_evidence=True)).strategy, "rag")

    def test_cross_tenant_and_stale_fail_closed(self):
        self.assertEqual(choose(replace(BASE, source_workspace="other")).strategy, "deny")
        self.assertEqual(choose(replace(BASE, source_fresh=False)).strategy, "deny")
        self.assertEqual(choose(replace(BASE, source_verified=False)).strategy, "deny")

    def test_missing_cache_falls_back_to_retrieval(self):
        self.assertEqual(choose(replace(BASE, prepared_context_available=False)).strategy, "rag")

    def test_invalid_budget_denied(self):
        self.assertEqual(choose(replace(BASE, context_budget=0)).strategy, "deny")
        self.assertEqual(choose(replace(BASE, corpus_tokens=True)).strategy, "deny")

if __name__ == "__main__":
    unittest.main()
