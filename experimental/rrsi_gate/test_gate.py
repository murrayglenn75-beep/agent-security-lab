import unittest
from dataclasses import replace

from experimental.rrsi_gate.gate import Candidate, assess

BASE = Candidate("exp1",("agent/planner.py",),"heldout-v1",
 (0.2,0.3,0.2,0.3),(0.8,0.9,0.8,0.9),
 (0.2,0.3,0.2,0.3),(0.8,0.9,0.8,0.9),
 1000,1050,True,True,True,True,"rollback-123")

class RRSIGateTests(unittest.TestCase):
 def test_strong_gain_is_eligible_only_advisory(self):
  self.assertTrue(assess(BASE).eligible)
 def test_rejects_overfit(self):
  c=replace(BASE,heldout_candidate=(0.2,0.3,0.2,0.3))
  self.assertIn("insufficient_heldout_gain",assess(c).reasons)
 def test_rejects_authority_and_benchmark_modification(self):
  for path in ("authority/rules.py","benchmarks/held_out/answers.json","../secrets","/.env"):
   self.assertIn("forbidden_path",assess(replace(BASE,changed_paths=(path,))).reasons)
 def test_security_approval_and_rollback(self):
  self.assertFalse(assess(replace(BASE,human_approved=False)).eligible)
  self.assertFalse(assess(replace(BASE,security_passed=False)).eligible)
  self.assertFalse(assess(replace(BASE,rollback_reference="")).eligible)
 def test_noise_and_cost_control(self):
  c=replace(BASE,heldout_candidate=(0.21,0.31,0.21,0.31))
  self.assertFalse(assess(c).eligible)
  c=replace(BASE,candidate_tokens=9000000)
  self.assertIn("cost_adjusted_gain",assess(c).reasons)
 def test_reused_failure_rejected(self):
  self.assertIn("previously_failed_candidate",assess(replace(BASE,failed_fingerprint=True)).reasons)

if __name__=="__main__":
 unittest.main()
