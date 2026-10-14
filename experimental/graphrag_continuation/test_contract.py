import unittest

from experimental.graphrag_continuation.contract import (
    Continuation,
    RelationCase,
    can_resume,
    compare,
)


class ContractTests(unittest.TestCase):
    def test_relationship_retrieval_improvement(self):
        case = RelationCase("q1", "tenant-a", ("doc-a",), ("other",), ("doc-a",),
                            {"doc-a": "tenant-a", "other": "tenant-a"})
        report = compare([case])
        self.assertEqual(report["baseline"]["recall_at_k"], 0.0)
        self.assertEqual(report["graph"]["recall_at_k"], 1.0)

    def test_cross_workspace_fails_closed(self):
        case = RelationCase("q1", "tenant-a", ("doc-a",), (), ("secret",),
                            {"doc-a": "tenant-a", "secret": "tenant-b"})
        with self.assertRaises(ValueError):
            compare([case])

    def test_resume_requires_every_guard(self):
        state = Continuation("job1", "local", "suspended", 200, 0, 2, True, True, "opaque-ref")
        self.assertTrue(can_resume(state, now_epoch=100, provider_id="local"))
        self.assertFalse(can_resume(state, now_epoch=200, provider_id="local"))
        self.assertFalse(can_resume(state, now_epoch=100, provider_id="cloud"))
        self.assertFalse(can_resume(Continuation("job1", "local", "suspended", 200, 0, 2,
                                                 False, True, "opaque-ref"),
                                    now_epoch=100, provider_id="local"))
        self.assertFalse(can_resume(Continuation("job1", "local", "suspended", 200, 0, 2,
                                                 True, False, "opaque-ref"),
                                    now_epoch=100, provider_id="local"))

    def test_exhausted_retry_or_missing_reference(self):
        t = Continuation("job1", "local", "suspended", 200, 2, 2, True, True, "ref")
        self.assertFalse(can_resume(t, now_epoch=100, provider_id="local"))
        self.assertFalse(can_resume(Continuation("job1", "local", "suspended", 200, 0, 2,
                                                 True, True, None),
                                    now_epoch=100, provider_id="local"))


if __name__ == "__main__":
    unittest.main()
