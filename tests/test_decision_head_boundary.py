import unittest
from decision_head_boundary import select_proposal


class DecisionBoundaryTests(unittest.TestCase):
    def test_abstain_below_threshold(self):
        self.assertEqual(select_proposal({"a": .7, "b": .3}, {"a", "b"}).reason, "low_confidence")

    def test_candidate_never_claims_authority(self):
        d = select_proposal({"a": .95, "b": .05}, {"a", "b"})
        self.assertFalse(d.abstained)
        self.assertEqual((d.choice, d.reason), ("a", "proposal_only_not_authorized"))

    def test_reject_unlisted_option(self):
        self.assertTrue(select_proposal({"a": .95, "b": .05}, {"a"}).abstained)

    def test_reject_nan(self):
        self.assertEqual(select_proposal({"a": float("nan")}, {"a"}).reason, "invalid_scores")

    def test_reject_nonprobabilities(self):
        self.assertEqual(select_proposal({"a": .9, "b": .9}, {"a", "b"}).reason, "not_normalized")

    def test_ambiguity(self):
        self.assertEqual(select_proposal({"a": .51, "b": .49}, {"a", "b"}, threshold=.5).reason, "ambiguous")

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            select_proposal({"a": 1.}, {"a"}, threshold=1.1)


if __name__ == "__main__":
    unittest.main()
