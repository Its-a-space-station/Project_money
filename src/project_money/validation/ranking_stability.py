"""Ranking / decision stability — verifier items V6 and V7.

A conclusion that flips when you change a defensible knob is not robust:
* V7 (cross-metric): a candidate ranking that reorders under a second reasonable
  performance metric is metric-dependent, not a finding (QuitoBench p. 28).
* V6 (threshold): a binarized accept/reject decision that flips under a small,
  pre-registered threshold sweep is knife-edge, not a decision (QuitoBench E.5).

Both share one core — the WORST pairwise agreement across the swept knob (the
weakest link, not the average: a single disagreeing pair is enough to make the
conclusion knob-dependent). Both flag ``needs_human_review``, not ``reject``: the
"right" metric or threshold may well exist, but a human must choose and justify it
rather than the gate silently killing or blessing the result. Necessary-not-
sufficient — compose with the edge-existence gates.

The metrics (V7) and the threshold sweep (V6), like the knobs ``min_agreement`` /
``max_flip_frac``, are pre-registration-load-bearing: chosen before seeing results,
or an anti-correlated metric can be dropped / the sweep narrowed to launder a pass.
The gate validates the knobs are well-formed but cannot enforce pre-registration.

Research-only: evaluates artifacts; it never acts.
"""

from __future__ import annotations

import math
from typing import Callable

import numpy as np
import pandas as pd

from project_money.validation.invariants import CheckResult, NEEDS_HUMAN_REVIEW, VALIDATION_PENDING

_MIN_CANDIDATES = 5


def _is_finite_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation (Pearson of ranks; ties get average ranks).
    NaN when either ranking is constant (correlation undefined)."""
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.std(ra) == 0 or np.std(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def _decision_agreement(a: np.ndarray, b: np.ndarray) -> float:
    """Fraction of items whose binary decision is identical across two thresholds."""
    return float(np.mean(a == b))


def _worst_pairwise(vectors: list, agree_fn: Callable[[np.ndarray, np.ndarray], float]) -> dict:
    """Worst (min) and mean pairwise agreement over ``vectors`` via ``agree_fn``."""
    pairs = [
        agree_fn(vectors[i], vectors[j])
        for i in range(len(vectors))
        for j in range(i + 1, len(vectors))
    ]
    finite = [p for p in pairs if math.isfinite(p)]
    if not finite:
        return {"min": float("nan"), "mean": float("nan"), "n_pairs": len(pairs), "n_finite": 0}
    return {
        "min": float(min(finite)),
        "mean": float(sum(finite) / len(finite)),
        "n_pairs": len(pairs),
        "n_finite": len(finite),
    }


def rank_agreement(score_sets) -> dict:
    """Worst/mean pairwise Spearman rank correlation across K score sets (each a
    length-N array of scores for the same N candidates). The shared V6/V7 core."""
    vecs = [np.asarray(s, dtype=float).ravel() for s in score_sets]
    return _worst_pairwise(vecs, _spearman)


def check_cross_metric_stability(
    metric_scores, *, min_agreement: float = 0.6, min_candidates: int = _MIN_CANDIDATES
) -> CheckResult:
    """Flag a candidate ranking that reorders across >= 2 performance metrics (V7).

    ``metric_scores`` is a dict ``{metric_name: scores}`` or a list of score arrays,
    each a length-N vector over the SAME N candidates. Fail-closed (``reject``) on
    < 2 metrics, ragged/short/non-finite scores, an out-of-range ``min_agreement``,
    or no metric pair with a defined ranking; ``needs_human_review`` when the worst
    pairwise Spearman falls below ``min_agreement``.
    """
    if not (_is_finite_number(min_agreement) and 0.0 <= min_agreement <= 1.0):
        return CheckResult(
            "cross_metric_stability", False, [f"min_agreement {min_agreement!r} must be in [0, 1] — fail closed"]
        )
    if isinstance(metric_scores, dict):
        arrays = [np.asarray(metric_scores[k], dtype=float).ravel() for k in metric_scores]
    else:
        arrays = [np.asarray(s, dtype=float).ravel() for s in metric_scores]
    if len(arrays) < 2:
        return CheckResult("cross_metric_stability", False, ["need >= 2 metrics to test ranking stability — fail closed"])
    n = len(arrays[0])
    if any(len(a) != n for a in arrays):
        return CheckResult("cross_metric_stability", False, ["metric score arrays differ in length — fail closed"])
    if n < min_candidates:
        return CheckResult(
            "cross_metric_stability", False,
            [f"too few candidates ({n} < {min_candidates}) to assess ranking stability — fail closed"],
        )
    if any(not np.all(np.isfinite(a)) for a in arrays):
        return CheckResult("cross_metric_stability", False, ["non-finite metric scores — fail closed"])

    agr = _worst_pairwise(arrays, _spearman)
    if agr["n_finite"] == 0:
        return CheckResult(
            "cross_metric_stability", False, ["no metric pair has a defined ranking (constant scores) — fail closed"]
        )
    if agr["min"] < min_agreement:
        return CheckResult(
            "cross_metric_stability", False,
            [f"candidate ranking is not stable across metrics (worst pairwise Spearman {agr['min']:.2f} < "
             f"{min_agreement:.2f}, mean {agr['mean']:.2f}) — the conclusion is metric-dependent; a human must "
             "justify which metric is authoritative"],
            NEEDS_HUMAN_REVIEW,
        )
    return CheckResult("cross_metric_stability", True, [])


def check_threshold_stability(
    scores,
    thresholds,
    *,
    higher_is_better: bool = True,
    max_flip_frac: float = 0.1,
    min_candidates: int = _MIN_CANDIDATES,
) -> CheckResult:
    """Flag a binarized accept/reject decision that flips under a pre-registered
    threshold sweep (V6).

    ``scores`` is a per-candidate continuous score; ``thresholds`` is the swept
    threshold set (pre-registered, typically a small perturbation of the operating
    point). A candidate is accepted iff ``score >= t`` (``higher_is_better``) else
    ``score <= t``. Fail-closed (``reject``) on too few candidates, < 2 thresholds,
    non-finite scores/thresholds, or an out-of-range ``max_flip_frac``;
    ``needs_human_review`` when the worst-case fraction of candidates that flip
    across the sweep exceeds ``max_flip_frac``.
    """
    if not (_is_finite_number(max_flip_frac) and 0.0 <= max_flip_frac <= 1.0):
        return CheckResult(
            "threshold_stability", False, [f"max_flip_frac {max_flip_frac!r} must be in [0, 1] — fail closed"]
        )
    s = np.asarray(scores, dtype=float).ravel()
    th = np.asarray(thresholds, dtype=float).ravel()
    if len(s) < min_candidates:
        return CheckResult(
            "threshold_stability", False, [f"too few candidates ({len(s)} < {min_candidates}) — fail closed"]
        )
    if not np.all(np.isfinite(s)):
        return CheckResult("threshold_stability", False, ["non-finite scores — fail closed"])
    if not np.all(np.isfinite(th)):
        return CheckResult("threshold_stability", False, ["non-finite threshold(s) — fail closed"])
    if len(np.unique(th)) < 2:
        # A duplicate / all-identical sweep sweeps nothing → decisions are trivially
        # identical → a vacuous PASS of the exact knife-edge V6 exists to catch.
        return CheckResult(
            "threshold_stability", False, ["need >= 2 distinct thresholds to sweep — fail closed"]
        )

    decisions = [(s >= t) if higher_is_better else (s <= t) for t in th]
    agr = _worst_pairwise(decisions, _decision_agreement)
    flip = 1.0 - agr["min"]  # worst-case fraction of candidates whose decision flips across the sweep
    if flip > max_flip_frac:
        return CheckResult(
            "threshold_stability", False,
            [f"binarized accept/reject decision is threshold-sensitive: up to {flip:.0%} of candidates flip "
             f"across the swept thresholds (> {max_flip_frac:.0%}) — knife-edge; a human must justify the threshold"],
            NEEDS_HUMAN_REVIEW,
        )
    # A "stable" verdict is only meaningful if the sweep actually brackets the data:
    # a sweep entirely above/below every score never probes the operating decision,
    # so its flip==0 is vacuous, not evidence of robustness.
    if not (th.max() >= s.min() and th.min() <= s.max()):
        return CheckResult(
            "threshold_stability", False,
            [f"the threshold sweep [{th.min():.4g}, {th.max():.4g}] lies entirely outside the score range "
             f"[{s.min():.4g}, {s.max():.4g}] — it never brackets the operating decision, so stability is "
             "unverifiable (not a pass)"],
            VALIDATION_PENDING,
        )
    return CheckResult("threshold_stability", True, [])
