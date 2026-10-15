import unittest

from experimental.layered_memory.rag_fixtures import RetrievalFixture, score


class RAGNegativeControls(unittest.TestCase):
    def test_answered_and_missing_evidence(self):
        labels = {"a": "team-a"}
        fixtures = (
            RetrievalFixture("q1", "team-a", labels, ("a",), ("a",), True),
            RetrievalFixture("q2", "team-a", labels, (), (), False),
        )
        report = score(fixtures)
        self.assertEqual(report["recall_at_k"], 1.0)
        self.assertEqual(report["unsupported_abstentions"], 1.0)

    def test_unauthorized_evidence_rejected(self):
        fixture = RetrievalFixture("q", "team-a", {"secret": "team-b"},
                                   ("secret",), ("secret",), True)
        with self.assertRaises(ValueError):
            score((fixture,))

    def test_unsupported_query_cannot_return_evidence(self):
        fixture = RetrievalFixture("unknown", "team-a", {"a": "team-a"}, (), ("a",), False)
        with self.assertRaises(ValueError):
            score((fixture,))


if __name__ == "__main__":
    unittest.main()
