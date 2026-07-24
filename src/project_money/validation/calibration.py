"""Calibration / process-fidelity axis — verifier item S26.

A NEW evaluation dimension the harness previously lacked (stock_market §6.4): point
metrics (accuracy, Sharpe, R²) say nothing about whether a model's *probabilities*
are trustworthy. Reliability-diagram binning measures the gap between predicted
confidence and realized frequency. It is **necessary-not-sufficient**: calibrated
probabilities are required to trust a probability-thresholded / size-by-confidence
strategy, but calibration alone never establishes an edge (a coin-flip forecaster
that always says 0.5 is perfectly calibrated and useless) — compose with the
edge-existence gates (deflated Sharpe, no-lookahead) and, for proper-scoring-rule
blow-ups on confident misses, ``prequential_log_loss``.

Design converged over two adversarial red-team rounds:
* **Bootstrap null band, not a fixed bar** (round-1). Uniform-bin ECE has a
  positive finite-sample bias (~sqrt(bins/2πN)); a fixed 0.1 bar rejects a *perfect*
  forecaster ~89% of the time at N=50. Observed statistics are compared to their
  distribution under perfect calibration (y' ~ Bernoulli(p), seeded → deterministic).
* **Per-bin studentized test with a family-wise null** (round-2). Count-weighted
  ECE forgives a sparse-but-confidently-wrong region, and a hard count floor just
  moves the seam (a ~19-sample all-wrong cluster still passed). Each bin's gap is
  studentized by its analytic Bernoulli noise (sd = sqrt(c(1-c)/n_b), c clipped to
  a floor so a saturated 0/1 bin isn't infinitely sensitive) and the *maximum*
  studentized gap is compared to its bootstrap null — the max statistic controls
  the multiple-testing inflation (8-13% → ~5%) that per-test bands caused.
* **Two binning resolutions** surface within-bin anti-calibration; **coverage on
  (pred,outcome) pairs** flags abstention; inputs are **sorted** for an
  order-invariant null. Residual (verification debt): anti-calibration hidden below
  the finest bin width, and small-N power loss, are inherent to binned estimation.

Research-only: evaluates artifacts; it never acts.
"""

from __future__ import annotations

import numpy as np

from project_money.validation.invariants import CheckResult, NEEDS_HUMAN_REVIEW, REJECT

_CONF_FLOOR = 0.05  # noise floor for per-bin sd, so saturated 0/1 bins aren't hair-trigger
_P_EPS = 1e-6


def _clean(pred_probs, outcomes) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(pred_probs, dtype=float).ravel()
    y = np.asarray(outcomes, dtype=float).ravel()
    return p, y


def _bin_mask(p: np.ndarray, lo: float, hi: float, first: bool) -> np.ndarray:
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


def check_calibration(
    pred_probs,
    outcomes,
    *,
    n_bins: int = 10,
    min_samples: int = 50,
    min_coverage: float = 0.8,
    n_bootstrap: int = 1000,
    null_quantile: float = 0.95,
    seed: int = 0,
) -> CheckResult:
    """Flag miscalibrated predicted probabilities (S26) — a review axis.

    Fail-closed on invalid inputs. Flags (each a mandatory audit; passing means
    "calibrated", NOT "has an edge"): low coverage on (pred,outcome) pairs; a
    per-bin studentized calibration gap beyond its family-wise perfect-calibration
    null (catches a confident-wrong sub-region at any count); and aggregate ECE
    beyond its (Šidák-adjusted) null band, at both ``n_bins`` and ``2*n_bins``.
    The bootstrap is seeded (deterministic).
    """
    p_raw, y_raw = _clean(pred_probs, outcomes)
    if len(p_raw) != len(y_raw):
        return CheckResult("calibration", False, [f"length mismatch ({len(p_raw)} vs {len(y_raw)}) — fail closed"])
    if len(p_raw) == 0:
        return CheckResult("calibration", False, ["no data — fail closed"])

    reasons: list[str] = []

    valid = ~(np.isnan(p_raw) | np.isnan(y_raw))
    coverage = float(np.mean(valid))
    if coverage < min_coverage:
        reasons.append(
            f"coverage {coverage:.2f} < {min_coverage} on (pred, outcome) pairs — "
            f"{(1 - coverage) * 100:.0f}% of cases are unresolved/abstained; calibration would be "
            "judged only on the answered subset (mandatory audit)"
        )

    p, y = p_raw[valid], y_raw[valid]
    if len(p) < min_samples:
        return CheckResult("calibration", False, [f"insufficient samples ({len(p)} < {min_samples}) — fail closed"])
    if ((p < 0.0) | (p > 1.0)).any():
        return CheckResult("calibration", False, ["predicted probabilities outside [0, 1] — fail closed"])
    if not set(np.unique(y).tolist()).issubset({0.0, 1.0}):
        return CheckResult("calibration", False, ["outcomes are not binary 0/1 — fail closed"])

    # Order-invariant bootstrap: sort so draws pair to samples deterministically.
    order = np.argsort(p, kind="stable")
    p, y = p[order], y[order]
    n = len(p)
    pc = np.clip(p, _P_EPS, 1.0 - _P_EPS)  # for Bernoulli draws
    binnings = (n_bins, 2 * n_bins)

    per_binning = []
    for nb in binnings:
        idx, counts, conf, acc = _binned_stats(p, y, nb)
        nz = counts > 0
        conf_clip = np.clip(conf, _CONF_FLOOR, 1.0 - _CONF_FLOOR)
        sd = np.sqrt(conf_clip * (1.0 - conf_clip) / np.maximum(counts, 1.0))
        obs_stud = np.where(nz, np.abs(acc - conf) / np.maximum(sd, 1e-12), 0.0)
        per_binning.append(
            {"nb": nb, "idx": idx, "counts": counts, "conf": conf, "nz": nz, "sd": sd,
             "obs_stud": obs_stud, "ece_obs": _ece(counts, conf, acc, n)}
        )

    rng = np.random.default_rng(seed)
    ece_null = {nb: np.empty(n_bootstrap) for nb in binnings}
    t_null = np.empty(n_bootstrap)  # family-wise studentized max across both binnings
    for b in range(n_bootstrap):
        yb = (rng.random(n) < pc).astype(float)
        tmax = 0.0
        for st in per_binning:
            nb, idx, counts, conf, nz, sd = (
                st["nb"], st["idx"], st["counts"], st["conf"], st["nz"], st["sd"]
            )
            accb = np.bincount(idx, weights=yb, minlength=nb) / np.maximum(counts, 1.0)
            gapb = np.abs(accb - conf)
            studb = np.where(nz, gapb / np.maximum(sd, 1e-12), 0.0)
            if nz.any():
                tmax = max(tmax, float(studb.max()))
            ece_null[nb][b] = float(np.sum((counts[nz] / n) * gapb[nz]))
        t_null[b] = tmax

    # Family-wise per-bin test (the max statistic already accounts for multiplicity).
    t_obs = max(float(st["obs_stud"].max()) for st in per_binning)
    t_bar = float(np.quantile(t_null, null_quantile))
    if t_obs > t_bar:
        worst = max(per_binning, key=lambda st: float(st["obs_stud"].max()))
        wi = int(np.argmax(worst["obs_stud"]))
        reasons.append(
            f"a calibration bin is systematically wrong beyond the perfect-calibration null "
            f"(studentized gap {t_obs:.1f} > {null_quantile:.0%} band {t_bar:.1f}; worst bin "
            f"{wi}/{worst['nb']}) — a confident sub-region is miscalibrated (mandatory audit)"
        )

    # Aggregate ECE, Šidák-adjusted for the two binning resolutions.
    q_ece = 1.0 - (1.0 - null_quantile) / len(binnings)
    for st in per_binning:
        bar = float(np.quantile(ece_null[st["nb"]], q_ece))
        if st["ece_obs"] > bar:
            reasons.append(
                f"ECE {st['ece_obs']:.3f} exceeds the perfect-calibration {q_ece:.1%} null band "
                f"{bar:.3f} at {st['nb']} bins — miscalibrated probabilities (mandatory audit; "
                "necessary-not-sufficient)"
            )

    # S26 is a review axis (necessary-not-sufficient): substantive miscalibration
    # is a mandatory audit, not an auto-reject; the fail-closed bad-input paths
    # above keep the default reject disposition.
    return CheckResult(
        "calibration", not reasons, reasons, NEEDS_HUMAN_REVIEW if reasons else REJECT
    )
