import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from experimental.rrsi_gate.evidence import manifest_for, verify_bundle
from experimental.rrsi_gate.test_gate import BASE


class EvidenceTests(unittest.TestCase):
    def test_valid_local_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "result.json").write_text('{"score": 0.9}')
            manifest = manifest_for({"result.json": (root / "result.json").read_bytes()},
                                    BASE.benchmark_id, BASE.rollback_reference)
            self.assertTrue(verify_bundle(root, manifest, BASE).eligible)

    def test_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "result.json").write_text("original")
            manifest = manifest_for({"result.json": b"original"},
                                    BASE.benchmark_id, BASE.rollback_reference)
            (root / "result.json").write_text("tampered")
            self.assertIn("artifact_hash_mismatch", verify_bundle(root, manifest, BASE).reasons)

    def test_path_traversal_and_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("../secret", "/tmp/absolute", "missing.txt"):
                manifest = manifest_for({name: b"test"}, BASE.benchmark_id, BASE.rollback_reference)
                self.assertFalse(verify_bundle(root, manifest, BASE).eligible)

    def test_mismatched_rollback_or_failed_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "test.txt").write_bytes(b"test")
            manifest = manifest_for({"test.txt": b"test"}, BASE.benchmark_id, "wrong")
            self.assertIn("manifest_mismatch", verify_bundle(root, manifest, BASE).reasons)
            manifest["rollback"] = BASE.rollback_reference
            self.assertFalse(verify_bundle(root, manifest, replace(BASE, human_approved=False)).eligible)


if __name__ == "__main__":
    unittest.main()
