import unittest
from dataclasses import replace

from discovery_gate import Claim, Evidence, assess, digest_bytes


def evidence(kind):
    return Evidence(kind, digest_bytes(kind.encode()), "fixture", "deterministic")


def claim(**changes):
    data = {"claim_id": "c1", "description": "test proposition",
            "source_url": "https://example.com/research",
            "source_version": "git-commit-example",
            "source_sha256": digest_bytes(b"source"),
            "generated_by": "model-a",
            "artifacts": (evidence("generation"),)}
    data.update(changes)
    return Claim(**data)


class DiscoveryGateTests(unittest.TestCase):
    def test_proposal(self):
        self.assertTrue(assess(claim())["gate_passed"])

    def test_reproduced_requires_reproduction(self):
        r = assess(claim(state="reproduced"))
        self.assertFalse(r["gate_passed"])
        self.assertIn("missing_reproduction", r["reasons"])

    def test_reproduced_with_artifact(self):
        r = assess(claim(state="reproduced", artifacts=(evidence("reproduction"),)))
        self.assertTrue(r["gate_passed"])

    def test_independent_requires_distinct_checker(self):
        r = assess(claim(state="independently_checked", independent_checker="model-a",
                         independent_method="second algorithm", human_reviewer="person",
                         artifacts=(evidence("reproduction"), evidence("independent_check"))))
        self.assertFalse(r["gate_passed"])

    def test_independent_with_metadata(self):
        r = assess(claim(state="independently_checked", independent_checker="reviewer-b",
                         independent_method="formal verification", human_reviewer="person",
                         artifacts=(evidence("reproduction"), evidence("independent_check"))))
        self.assertTrue(r["gate_passed"])

    def test_bad_digest(self):
        self.assertFalse(assess(claim(source_sha256="not-a-digest"))["gate_passed"])

    def test_unknown_state(self):
        self.assertFalse(assess(claim(state="verified_by_ai"))["gate_passed"])

    def test_empty_artifacts(self):
        self.assertFalse(assess(claim(artifacts=()))["gate_passed"])

    def test_self_correction_rejected(self):
        self.assertFalse(assess(claim(correction_of="c1"))["gate_passed"])

    def test_digest_input_type(self):
        with self.assertRaises(TypeError):
            digest_bytes("text")


if __name__ == "__main__":
    unittest.main()
