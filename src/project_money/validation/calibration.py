"""Calibration / process-fidelity axis — verifier item S26.

A NEW evaluation dimension the harness previously lacked (stock_market §6.4,
motivated by the "Has-the-DNN-learnt" line of work): point metrics (accuracy,
Sharpe, R²) say nothing about whether a model's *probabilities* are trustworthy.
Reliability-diagram binning measures the gap between predicted confidence and
realized frequency. It is **necessary-not-sufficient**: well-calibrated
probabilities are required to trust any probability-thresholded or
size-by-confidence strategy, but calibration alone never establishes an edge (a
coin-flip forecaster that always says 0.5 is perfectly calibrated and useless) —
compose with the edge-existence gates (deflated Sharpe, no-lookahead) and, for
proper-scoring-rule blow-ups on confident misses, ``prequential_log_loss``.

Design hardened after an adversarial red-team, which showed a fixed ECE bar is
both too tight and too loose:
* **Bootstrap null band, not a fixed bar** (round-1 Findings 1 & 5). Uniform-bin
  ECE has a positive finite-sample bias (~sqrt(bins / 2πN)), so a fixed 0.1
  threshold rejects a *perfect* forecaster ~89% of the time at N=50. We instead
  compare observed ECE/MCE to their distribution under perfect calibration
  (y' ~ Bernoulli(p), seeded → deterministic) and flag only beyond the null band.
* **MCE with a per-bin count floor** (Finding 2). Count-weighted ECE forgives a
  sparse-but-confidently-wrong region (~10% of the book maximally wrong still
  passes) — exactly where a confidence-sized strategy levers up. Max Calibration
  Error over adequately-populated bins catches it.
* **A finer-binning pass** (Finding 3). Uniform ECE can be blind to
  anti-calibration *within* a wide bin; a 2×-bins pass surfaces it.
* **A coverage floor** (Finding 4). A forecaster that abstains (NaN) on most cases
  can look calibrated on the few it answers; coverage is checked before ECE.

Research-only: evaluates artifacts; it never acts.
"""

from __future__ import annotations

import numpy as np

from project_money.validation.invariants import CheckResult


def _clean(pred_probs, outcomes) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(pred_probs, dtype=float).ravel()
    y = np.asarray(outcomes, dtype=float).ravel()
    return p, y


def _bin_mask(p: np.ndarray, lo: float, hi: float, first: bool) -> np.ndarray:
    # Half-open (lo, hi] except the first bin includes its lower edge.
    return (p >= lo) & (p <= hi) if first else (p > lo) & (p <= hi)


def reliability_curve(pred_probs, outcomes, *, n_bins: int = 10) -> list[tuple[float, float, float, float, int]]:
    """Per-bin ``(bin_lo, bin_hi, mean_pred, mean_outcome, count)`` for a reliability
    diagram; ``mean_pred``/``mean_outcome`` are NaN for empty bins."""
    p, y = _clean(pred_probs, outcomes)
    mask = ~(np.isnan(p) | np.isnan(y))
    p, y = p[mask], y[mask]
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    curve: list[tuple[float, float, float, float, int]] = []
    for i in range(n_bins):
        lo, hi = float(edges[i]), float(edges[i + 1])
        in_bin = _bin_mask(p, lo, hi, i == 0)
        cnt = int(in_bin.sum())
        if cnt == 0:
            curve.append((lo, hi, float("nan"), float("nan"), 0))
        else:
            curve.append((lo, hi, float(p[in_bin].mean()), float(y[in_bin].mean()), cnt))
    return curve


def expected_calibration_error(pred_probs, outcomes, *, n_bins: int = 10) -> float:
    """Uniform-binning ECE: ``sum_b (n_b/N) * |acc_b - conf_b|``. NaN if no valid
    pairs. 0 = perfectly calibrated; higher = worse."""
    p, y = _clean(pred_probs, outcomes)
    mask = ~(np.isnan(p) | np.isnan(y))
    p, y = p[mask], y[mask]
    if len(p) == 0:
        return float("nan")
    _, counts, conf, acc = _binned_stats(p, y, n_bins)
    return _ece(counts, conf, acc, len(p))


def _binned_stats(p: np.ndarray, y: np.ndarray, n_bins: int):
    """Bin index per sample + per-bin (count, mean-pred, mean-outcome). Binning
    matches ``reliability_curve``: (lo, hi], first bin includes 0."""
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(p, edges, right=True), 1, n_bins) - 1
    counts = np.bincount(idx, minlength=n_bins).astype(float)
    safe = np.maximum(counts, 1.0)
    conf = np.bincount(idx, weights=p, minlength=n_bins) / safe
    acc = np.bincount(idx, weights=y, minlength=n_bins) / safe
    return idx, counts, conf, acc


def _ece(counts: np.ndarray, conf: np.ndarray, acc: np.ndarray, n: int) -> float:
    nz = counts > 0
    return float(np.sum((counts[nz] / n) * np.abs(acc[nz] - conf[nz])))


def _mce(counts: np.ndarray, conf: np.ndarray, acc: np.ndarray, *, count_floor: int) -> float:
    floored = counts >= count_floor
    return float(np.abs(acc[floored] - conf[floored]).max()) if floored.any() else 0.0


def check_calibration(
    pred_probs,
    outcomes,
    *,
    n_bins: int = 10,
    min_samples: int = 50,
    min_coverage: float = 0.8,
    mce_count_floor: int = 20,
    n_bootstrap: int = 500,
    null_quantile: float = 0.95,
    seed: int = 0,
) -> CheckResult:
    """Flag miscalibrated predicted probabilities (S26) — a review axis.

    Fail-closed on invalid inputs. Flags (each a mandatory audit; passing means
    "calibrated", NOT "has an edge"): low coverage (abstention); ECE or MCE beyond
    the perfect-calibration bootstrap null band, at both ``n_bins`` and ``2*n_bins``
    resolutions. The bootstrap is seeded (deterministic).
    """
    p_raw, y_raw = _clean(pred_probs, outcomes)
    if len(p_raw) != len(y_raw):
        return CheckResult("calibration", False, [f"length mismatch ({len(p_raw)} vs {len(y_raw)}) — fail closed"])
    if len(p_raw) == 0:
        return CheckResult("calibration", False, ["no data — fail closed"])

    reasons: list[str] = []

    coverage = float(np.mean(~np.isnan(p_raw)))
    if coverage < min_coverage:
        reasons.append(
            f"coverage {coverage:.2f} < {min_coverage} — the forecaster abstains (NaN) on "
            f"{(1 - coverage) * 100:.0f}% of cases; calibration would be judged only on answered "
            "calls (mandatory audit)"
        )

    mask = ~(np.isnan(p_raw) | np.isnan(y_raw))
    p, y = p_raw[mask], y_raw[mask]
    if len(p) < min_samples:
        return CheckResult("calibration", False, [f"insufficient samples ({len(p)} < {min_samples}) — fail closed"])
    if ((p < 0.0) | (p > 1.0)).any():
        return CheckResult("calibration", False, ["predicted probabilities outside [0, 1] — fail closed"])
    if not set(np.unique(y).tolist()).issubset({0.0, 1.0}):
        return CheckResult("calibration", False, ["outcomes are not binary 0/1 — fail closed"])

    n = len(p)
    rng = np.random.default_rng(seed)
    for nb in (n_bins, 2 * n_bins):
        idx, counts, conf, acc = _binned_stats(p, y, nb)
        ece_obs = _ece(counts, conf, acc, n)
        mce_obs = _mce(counts, conf, acc, count_floor=mce_count_floor)

        # Parametric-bootstrap null under perfect calibration: y' ~ Bernoulli(p).
        safe = np.maximum(counts, 1.0)
        floored = counts >= mce_count_floor
        nz = counts > 0
        ece_null = np.empty(n_bootstrap)
        mce_null = np.empty(n_bootstrap)
        for b in range(n_bootstrap):
            yb = (rng.random(n) < p).astype(float)
            accb = np.bincount(idx, weights=yb, minlength=nb) / safe
            gapb = np.abs(accb - conf)
            ece_null[b] = np.sum((counts[nz] / n) * gapb[nz])
            mce_null[b] = float(gapb[floored].max()) if floored.any() else 0.0
        ece_bar = float(np.quantile(ece_null, null_quantile))
        mce_bar = float(np.quantile(mce_null, null_quantile))

        if ece_obs > ece_bar:
            reasons.append(
                f"ECE {ece_obs:.3f} exceeds the perfect-calibration {null_quantile:.0%} null band "
                f"{ece_bar:.3f} at {nb} bins — miscalibrated probabilities (mandatory audit; "
                "necessary-not-sufficient)"
            )
        if mce_obs > mce_bar:
            reasons.append(
                f"MCE {mce_obs:.3f} (bins with >= {mce_count_floor} samples) exceeds null band "
                f"{mce_bar:.3f} at {nb} bins — a confident sub-region is systematically wrong "
                "(mandatory audit)"
            )

    return CheckResult("calibration", not reasons, reasons)
