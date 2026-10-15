import hashlib
import unittest
from dataclasses import replace

from experimental.layered_memory.memory import Node, recall, validate


class LayeredMemoryTests(unittest.TestCase):
    def setUp(self):
        self.raw = b"Failed tasks retry three times"
        digest = hashlib.sha256(self.raw).hexdigest()
        self.source = {("team-a", "log-1"): self.raw}
        self.nodes = (
            Node("conversation", "team-a", 0, "raw conversation", "log-1", digest),
            Node("fact", "team-a", 1, "retry three times", "log-1", digest, ("conversation",)),
            Node("scenario", "team-a", 2, "task retry policy", "log-1", digest, ("fact",)),
        )

    def test_evidence_grounded_recall(self):
        result = recall(self.nodes, self.source, "team-a", ("retry",))
        self.assertEqual(tuple(x.node_id for x in result), ("fact", "scenario"))

    def test_missing_and_modified_evidence(self):
        with self.assertRaises(ValueError):
            validate(self.nodes, {}, "team-a")
        with self.assertRaises(ValueError):
            validate(self.nodes, {("team-a", "log-1"): b"changed"}, "team-a")

    def test_cross_workspace_denied(self):
        with self.assertRaises(ValueError):
            recall(self.nodes, self.source, "team-b", ("retry",))

    def test_bad_parent_denied(self):
        broken = self.nodes[:2] + (replace(self.nodes[2], parent_ids=("missing",)),)
        with self.assertRaises(ValueError):
            validate(broken, self.source, "team-a")


if __name__ == "__main__":
    unittest.main()
