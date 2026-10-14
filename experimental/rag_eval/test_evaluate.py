import unittest
from experimental.rag_eval.evaluate import Case, evaluate

class TestRagEvaluation(unittest.TestCase):
    def test_perfect(self):
        d=evaluate([Case("q",("a",),("a","b"),("a",),2,2)])
        for k in ("recall_at_k","mrr_at_k","ndcg_at_k","citation_precision","claim_support"):
            self.assertEqual(d[k],1.0)
    def test_no_matches(self):
        d=evaluate([Case("q",("a",),("b",),("b",),0,1)])
        for k in ("recall_at_k","mrr_at_k","ndcg_at_k","citation_precision","claim_support"):
            self.assertEqual(d[k],0.0)
    def test_order_sensitive_ranking(self):
        d=evaluate([Case("q",("a",),("b","a"))],2)
        self.assertEqual(d["mrr_at_k"],0.5)
        self.assertGreater(d["ndcg_at_k"],0.0)
        self.assertLess(d["ndcg_at_k"],1.0)
    def test_missing_citation_labels_are_not_evaluated(self):
        d=evaluate([Case("q",("a",),("a",))])
        self.assertIsNone(d["citation_precision"])
        self.assertIsNone(d["claim_support"])
    def test_fail_closed_on_invalid_labels(self):
        with self.assertRaises(ValueError): evaluate([])
        with self.assertRaises(ValueError): evaluate([Case("q",("a",),("a","a"))])
        with self.assertRaises(ValueError): evaluate([Case("q",("a",),("a",),(),2,1)])

if __name__=="__main__": unittest.main()
