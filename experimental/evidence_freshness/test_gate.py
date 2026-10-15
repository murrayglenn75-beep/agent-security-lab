import hashlib
import unittest
from dataclasses import replace

from experimental.evidence_freshness.gate import Assertion, Source, assess_history, check

RAW = b"retry count = 3"
DIGEST = hashlib.sha256(RAW).hexdigest()
CLAIM = Assertion("c1", "team-a", "src1", "v1", DIGEST)
SOURCES = {("team-a", "src1"): Source("team-a", "src1", "v1", RAW)}


class FreshnessTests(unittest.TestCase):
    def test_unchanged_bytes_and_version(self):
        self.assertEqual(check(CLAIM, SOURCES, workspace_id="team-a").status, "verified")

    def test_changed_bytes_version_and_missing_source(self):
        changed = {("team-a", "src1"): Source("team-a", "src1", "v1", b"changed")}
        self.assertEqual(check(CLAIM, changed, workspace_id="team-a").reason, "bytes_changed")
        version = {("team-a", "src1"): Source("team-a", "src1", "v2", RAW)}
        self.assertEqual(check(CLAIM, version, workspace_id="team-a").reason, "version_changed")
        self.assertEqual(check(CLAIM, {}, workspace_id="team-a").reason, "source_missing")

    def test_workspace_isolation(self):
        self.assertEqual(check(CLAIM, SOURCES, workspace_id="team-b").reason, "workspace_mismatch")
        result = assess_history((CLAIM,), SOURCES, workspace_id="team-b")
        self.assertEqual(result, {})

    def test_superseded_claim_history(self):
        new = replace(CLAIM, claim_id="c2", supersedes="c1")
        result = assess_history((CLAIM, new), SOURCES, workspace_id="team-a")
        self.assertEqual(result["c1"].reason, "superseded_by_newer_assertion")
        self.assertEqual(result["c2"].status, "verified")

    def test_conflicts_fail_closed(self):
        conflict = replace(CLAIM, claim_id="c2")
        result = assess_history((CLAIM, conflict), SOURCES, workspace_id="team-a")
        self.assertEqual(result["c1"].reason, "unresolved_competing_claims")
        self.assertEqual(result["c2"].status, "untrusted")

    def test_disputed_and_forged_hash_not_trusted(self):
        self.assertEqual(check(replace(CLAIM, status="disputed"), SOURCES,
                               workspace_id="team-a").status, "untrusted")
        self.assertEqual(check(replace(CLAIM, source_sha256="bad"), SOURCES,
                               workspace_id="team-a").status, "untrusted")


if __name__ == "__main__":
    unittest.main()
