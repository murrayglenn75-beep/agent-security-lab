import unittest
from dataclasses import replace

from experimental.agent_eval.benchmark import FIXTURES, assess


class AgentEvaluationTests(unittest.TestCase):
    def test_reference_fixtures(self):
        result = assess(FIXTURES)
        self.assertEqual(result["unauthorized_effects"], 0)
        self.assertEqual(result["unsafe_answers"], 0)
        self.assertEqual(result["retrieval"]["recall_at_k"], 1.0)
        self.assertEqual(result["decisions"][1]["strategy"], "deny")

    def test_unauthorized_effect_detected(self):
        t = replace(FIXTURES[1], effect_occurred=True)
        self.assertEqual(assess((t,))["unauthorized_effects"], 1)

    def test_unsupported_non_abstention_detected(self):
        t = replace(FIXTURES[3], abstained=False)
        self.assertEqual(assess((t,))["unsafe_answers"], 1)

    def test_duplicate_trials_rejected(self):
        with self.assertRaises(ValueError):
            assess((FIXTURES[0], FIXTURES[0]))


if __name__ == "__main__":
    unittest.main()
