import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engineering.offline_trace_replay import TraceStep, replay_decisions


class TraceReplayTests(unittest.TestCase):
    def test_matching_denial(self):
        self.assertTrue(replay_decisions((TraceStep("e1", "r1", "read", False, False),)).accepted)

    def test_unauthorized_grant_detected(self):
        self.assertEqual(replay_decisions((TraceStep("e1", "r1", "network", False, True),)).reason, "authorization_regression")

    def test_wrongly_denied_detected(self):
        self.assertFalse(replay_decisions((TraceStep("e1", "r1", "read", True, False),)).accepted)

    def test_duplicate_event_denied(self):
        rows=(TraceStep("e1", "r1", "a", False, False),TraceStep("e1","r2","b",False,False))
        self.assertEqual(replay_decisions(rows).reason,"duplicate_event_id")

    def test_empty_trace_denied(self):
        self.assertFalse(replay_decisions(()).accepted)

    def test_limit_denied(self):
        rows=(TraceStep("e1","r1","a",False,False),TraceStep("e2","r2","b",False,False))
        self.assertEqual(replay_decisions(rows,maximum=1).reason,"invalid_trace_size")

    def test_no_action_payload_denied(self):
        self.assertFalse(replay_decisions((TraceStep("e1","r1","",False,False),)).accepted)


if __name__ == "__main__":
    unittest.main()
