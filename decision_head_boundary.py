"""Evaluation-only adapter for externally trained decision heads.

Scores are *not* authorization. The caller must send any selected proposal
through its independent policy/approval/effect boundary.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Optional


@dataclass(frozen=True)
class Decision:
    choice: Optional[str]
    abstained: bool
    reason: str
    confidence: float


def select_proposal(
    scores: Mapping[str, float],
    allowed_options: set[str],
    *,
    threshold: float = 0.9,
    margin: float = 0.1,
) -> Decision:
    """Select among bounded options, otherwise abstain.

    Scores must be already calibrated by an independently evaluated model.
    This adapter does not train, calibrate, or certify those scores.
    """
    if not (isfinite(threshold) and 0 < threshold <= 1):
        raise ValueError("invalid threshold")
    if not (isfinite(margin) and 0 <= margin <= 1):
        raise ValueError("invalid margin")
    if not scores or not allowed_options or set(scores) != allowed_options:
        return Decision(None, True, "option_set_mismatch", 0.0)
    if any(not isinstance(v, (int, float)) or not isfinite(v) or v < 0 or v > 1 for v in scores.values()):
        return Decision(None, True, "invalid_scores", 0.0)
    if abs(sum(scores.values()) - 1.0) > 1e-6:
        return Decision(None, True, "not_normalized", 0.0)
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    best, confidence = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else 0.0
    if confidence < threshold:
        return Decision(None, True, "low_confidence", confidence)
    if confidence - runner_up < margin:
        return Decision(None, True, "ambiguous", confidence)
    return Decision(best, False, "proposal_only_not_authorized", confidence)
