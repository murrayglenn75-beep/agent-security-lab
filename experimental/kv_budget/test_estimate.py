import unittest
from experimental.kv_budget.estimate import CacheShape, kv_bytes, budget

class CacheTests(unittest.TestCase):
    def test_conventional_float16(self):
        self.assertEqual(kv_bytes(CacheShape(32,32,128,1024,2,2)), 536870912)

    def test_gqa_and_cache_precision_reduce_estimate(self):
        full=CacheShape(32,32,128,1024,2,2)
        gqa=CacheShape(32,8,128,1024,2,2)
        self.assertEqual(kv_bytes(gqa)*4,kv_bytes(full))
        self.assertEqual(kv_bytes(CacheShape(32,8,128,1024,1,1))*2,kv_bytes(gqa))

    def test_budget_fail_closed(self):
        s=CacheShape(32,32,128,1024,2,2)
        self.assertFalse(budget(s,model_bytes=15_000_000_000,overhead_bytes=1_000_000_000,ram_bytes=16_000_000_000)["fits_estimate"])
        with self.assertRaises(ValueError):
            kv_bytes(CacheShape(32,8,128,-1,2,2))

if __name__=="__main__":
    unittest.main()
