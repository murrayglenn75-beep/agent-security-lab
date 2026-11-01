import unittest
from hashlib import sha256

from engineering.governed_skills_admission import SkillManifest, admit_skill


class SkillAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.data = b"# read-only skill"
        self.digest = sha256(self.data).hexdigest()
        self.skill = SkillManifest("audit", "1.0", self.digest, frozenset({"read"}))

    def test_approved(self):
        self.assertTrue(admit_skill(self.skill, self.data, self.digest, frozenset({"read"})).accepted)

    def test_no_approval(self):
        self.assertFalse(admit_skill(self.skill, self.data, None, frozenset({"read"})).accepted)

    def test_modified_payload(self):
        self.assertEqual(admit_skill(self.skill, b"modified", self.digest, frozenset({"read"})).reason, "content_changed")

    def test_wrong_approval_digest(self):
        self.assertEqual(admit_skill(self.skill, self.data, "0" * 64, frozenset({"read"})).reason, "approval_mismatch")

    def test_capability_expansion(self):
        changed = SkillManifest("audit", "1.0", self.digest, frozenset({"write"}))
        self.assertEqual(admit_skill(changed, self.data, self.digest, frozenset({"read"})).reason, "capability_expansion")

    def test_invalid_manifest_digest(self):
        changed = SkillManifest("audit", "1.0", "oops", frozenset({"read"}))
        self.assertFalse(admit_skill(changed, self.data, self.digest, frozenset({"read"})).accepted)

    def test_invalid_identity(self):
        changed = SkillManifest("", "1.0", self.digest, frozenset({"read"}))
        self.assertFalse(admit_skill(changed, self.data, self.digest, frozenset({"read"})).accepted)


if __name__ == "__main__":
    unittest.main()
