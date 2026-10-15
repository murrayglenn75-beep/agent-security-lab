"""Advisory RRSI experiment eligibility; cannot execute or authorize promotion."""
from __future__ import annotations

import math
from dataclasses import dataclass

FORBIDDEN = ("authority/", "policies/", "secrets/", ".github/workflows/", "benchmarks/held_out/")
@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    changed_paths: tuple[str, ...]
    benchmark_id: str
    baseline_scores: tuple[float, ...]
    candidate_scores: tuple[float, ...]
    heldout_baseline: tuple[float, ...]
    heldout_candidate: tuple[float, ...]
    baseline_tokens: int
    candidate_tokens: int
    security_passed: bool
    leakage_screen_passed: bool
    independent_reviewed: bool
    human_approved: bool
    rollback_reference: str
    failed_fingerprint: bool = False

@dataclass(frozen=True)
class Verdict:
    eligible: bool
    reasons: tuple[str, ...]

def assess(c: Candidate, *, max_changed: int = 3, min_gain: float = 0.02,
           noise_floor: float = 0.01, token_penalty: float = 0.01) -> Verdict:
    reasons: list[str] = []
    if not c.candidate_id or not c.benchmark_id or not c.rollback_reference:
        reasons.append("missing_provenance_or_rollback")
    if not c.changed_paths or len(c.changed_paths) > max_changed or len(set(c.changed_paths)) != len(c.changed_paths):
        reasons.append("change_budget")
    for path in c.changed_paths:
        if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or ".." in path.split("/") or path.startswith(FORBIDDEN):
            reasons.append("forbidden_path")
            break
    if c.failed_fingerprint:
        reasons.append("previously_failed_candidate")
    if c.security_passed is not True or c.leakage_screen_passed is not True:
        reasons.append("security_or_leakage")
    if c.independent_reviewed is not True or c.human_approved is not True:
        reasons.append("review_or_approval")
    groups = (c.baseline_scores,c.candidate_scores,c.heldout_baseline,c.heldout_candidate)
    if any(not isinstance(x, tuple) or len(x)<3 or any(type(v) not in (float,int) or not math.isfinite(v) or not 0<=v<=1 for v in x) for x in groups):
        reasons.append("invalid_evaluation")
    elif len(c.baseline_scores)!=len(c.candidate_scores) or len(c.heldout_baseline)!=len(c.heldout_candidate):
        reasons.append("unpaired_evaluation")
    else:
        train = sum(a-b for a,b in zip(c.candidate_scores,c.baseline_scores))/len(c.baseline_scores)
        heldout = [a-b for a,b in zip(c.heldout_candidate,c.heldout_baseline)]
        gain = sum(heldout)/len(heldout)
        # Conservative paired standard-error floor, not a statistical significance proof.
        sem = (math.sqrt(sum((v-gain)**2 for v in heldout)/(len(heldout)-1))/math.sqrt(len(heldout)))
        if train > 0 and gain <= 0:
            reasons.append("overfit")
        if gain - 2*sem <= max(min_gain,noise_floor):
            reasons.append("insufficient_heldout_gain")
    if type(c.baseline_tokens) is not int or type(c.candidate_tokens) is not int or c.baseline_tokens<=0 or c.candidate_tokens<=0:
        reasons.append("invalid_cost")
    elif ("invalid_evaluation" not in reasons and "unpaired_evaluation" not in reasons
          and gain - 2*sem - token_penalty*max(0,(c.candidate_tokens-c.baseline_tokens)/c.baseline_tokens) <= max(min_gain,noise_floor)):
        reasons.append("cost_adjusted_gain")
    return Verdict(not reasons,tuple(dict.fromkeys(reasons)))
