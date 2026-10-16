import unittest
from src.tenant_isolation import Chunk, search_scoped, cache_key, canary_probe

class TenantIsolationTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            Chunk("tenant-a", "a1", "private-canary-6a9b confidential"),
            Chunk("tenant-b", "b1", "ordinary content"),
        ]
    def test_cross_tenant_canary_not_visible(self):
        self.assertFalse(canary_probe(self.docs, "tenant-a", "tenant-b",
                                      "private-canary-6a9b")["leak_detected"])
    def test_self_tenant_retrieves(self):
        self.assertEqual(len(search_scoped("tenant-a", self.docs, lambda _: True)), 1)
    def test_cache_partitions(self):
        self.assertNotEqual(cache_key("tenant-a", "same question"),
                            cache_key("tenant-b", "same question"))
    def test_empty_tenant_denied(self):
        with self.assertRaises(ValueError):
            search_scoped("", self.docs, lambda _: True)
    def test_no_unscoped_zero_hit_retry(self):
        self.assertEqual(search_scoped("tenant-b", self.docs, lambda t: "canary" in t), [])
    def test_missing_canary_is_not_a_pass(self):
        with self.assertRaisesRegex(ValueError, "canary_not_planted"):
            canary_probe(self.docs, "tenant-a", "tenant-b", "nonexistent-marker")
    def test_same_tenant_probe_is_invalid(self):
        with self.assertRaises(ValueError):
            canary_probe(self.docs, "tenant-a", "tenant-a", "private-canary-6a9b")
if __name__ == "__main__":
    unittest.main()
