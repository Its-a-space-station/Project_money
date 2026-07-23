"""Forecast-quality sanity diagnostics — verifier items S5 and S10.

Two structural checks the corpus flagged as GAPS (stock_market_synthesis §5.2,
§6.1), targeting the Nabipour specimen (R²≈1.0 on price levels, error flat across
horizons) and the FNSPID / Robust-DL near-perfect-on-levels family.

S5 (returns-not-levels) is a forecast-*metric-honesty* check — NOT the primary
contemporaneous-leak defense (that is ``check_no_lookahead`` and the S6 intra-bar
detector). It catches: near-perfect-on-levels mirages, repackaged persistence, and
implausibly high fit. A contemporaneous leak that beats persistence by a *plausible*
margin on a level series, and overlapping/smoothed-return targets (which need
de-overlapped evaluation), are out of scope here by design — flagged elsewhere.

Level-ness is inferred from *integratedness* (variance growth with window), not
lag-1 autocorrelation, so overlapping/smoothed returns and mean-reverting levels
are not misclassified. Three regimes (``is_levels`` is a hint that only selects the
integrated regime; it never disables the FN-guarding R² checks):
  - integrated (random-walk level): persistence-skill test + level-lag fingerprint;
  - autocorrelated-but-stationary (overlapping/smoothed returns): abstain (only the
    unconditional implausible-R² backstop), to avoid false-flagging a legitimate
    target class the (y_true, y_pred) pair cannot be judged on here;
  - low-autocorrelation returns: a returns R² bar (an honest returns forecast has
    R² ≈ 0.01–0.05, so a high R² is leakage).

S10 (horizon monotonicity) is a **review flag**: OOS error should grow with horizon;
a decreasing (inverted), flat, or grow-only-at-one-endpoint curve is a leakage
fingerprint (or an unpredictable series — adjudicate with a skill-vs-null check).

Hardened over two adversarial red-team rounds (exploits kept as regression
specimens). Research-only: evaluates artifacts; it never acts.
"""

from __future__ import annotations

import numpy as np

from project_money.validation.invariants import CheckResult

_MIN_SAMPLE = 10


def _aligned(y_true, y_pred) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(y_true, dtype=float).ravel()
    b = np.asarray(y_pred, dtype=float).ravel()
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    mask = ~(np.isnan(a) | np.isnan(b))
    return a[mask], b[mask]


def r_squared(y_true, y_pred) -> float:
    """Coefficient of determination; NaN when the target has no variance."""
    a, b = _aligned(y_true, y_pred)
    if len(a) < 2:
        return float("nan")
    ss_tot = float(np.sum((a - a.mean()) ** 2))
    if ss_tot == 0.0:
        return float("nan")
    ss_res = float(np.sum((a - b) ** 2))
    return 1.0 - ss_res / ss_tot


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _lag1_autocorr(a: np.ndarray) -> float:
    """Lag-1 autocorrelation of the target — high for both levels and overlapping
    returns (so it selects persistence-strength regime, not integration)."""
    return _corr(a[1:], a[:-1]) if len(a) >= 3 else float("nan")


def _integratedness(a: np.ndarray) -> float:
    """Ratio of whole-series variance to mean within-quarter variance. Large
    (>~2) for an integrated / random-walk series (variance grows with the window);
    ≈1 for a stationary series (daily returns, overlapping returns, mean-reverting
    levels). Distinguishes true integration from high-autocorrelation-but-
    stationary series, which lag-1 autocorrelation alone cannot."""
    n = len(a)
    if n < 8:
        return float("nan")
    quarters = [q for q in np.array_split(a, 4) if len(q) > 1]
    within = float(np.mean([np.var(q) for q in quarters])) if quarters else 0.0
    whole = float(np.var(a))
    if within == 0.0:
        return float("inf")
    return whole / within


def _persistence_skill(a: np.ndarray, b: np.ndarray) -> float:
    """1 − MSE_model / MSE_persistence, where persistence predicts y_t with
    y_{t-1}. >0 beats the naive last-value null; ≈1 is implausibly perfect."""
    if len(a) < 3:
        return float("nan")
    target, pred, persist = a[1:], b[1:], a[:-1]
    mse_persist = float(np.mean((target - persist) ** 2))
    if mse_persist == 0.0:
        return float("nan")
    return 1.0 - float(np.mean((target - pred) ** 2)) / mse_persist


def check_returns_not_levels(
    y_true,
    y_pred,
    *,
    is_levels: bool | None = None,
    max_r2: float = 0.99,
    returns_r2_bar: float = 0.15,
    min_persistence_skill: float = 0.0,
    integrated_skill_bar: float = 0.5,
    integratedness_threshold: float = 2.0,
    autocorr_threshold: float = 0.5,
    lag_corr_threshold: float = 0.99,
) -> CheckResult:
    """Flag misleading level fits, repackaged persistence, and implausible fits (S5).

    See the module docstring for scope and the three-regime design. ``is_levels`` is
    a hint that only forces the integrated regime; it cannot disable the
    unconditional or returns R² checks. Fail-closed on < ``_MIN_SAMPLE`` samples.
    """
    a, b = _aligned(y_true, y_pred)
    if len(a) < _MIN_SAMPLE:
        return CheckResult(
            "returns_not_levels", False, [f"insufficient sample ({len(a)} < {_MIN_SAMPLE}) — fail closed"]
        )

    reasons: list[str] = []

    r2 = r_squared(a, b)
    if np.isfinite(r2) and r2 > max_r2:
        reasons.append(
            f"R²={r2:.5f} exceeds {max_r2} — implausibly high for any honest OOS forecast "
            "(leakage or a level fit reported as skill); checked regardless of is_levels"
        )

    integ = _integratedness(a)
    acf1 = _lag1_autocorr(a)
    integrated = (is_levels is True) or (
        is_levels is None and np.isfinite(integ) and integ > integratedness_threshold
    )
    autocorrelated_stationary = (
        not integrated and np.isfinite(acf1) and acf1 > autocorr_threshold
    )

    if integrated:
        skill = _persistence_skill(a, b)
        if np.isfinite(skill):
            if skill <= min_persistence_skill:
                reasons.append(
                    f"persistence skill {skill:.3f} ≤ {min_persistence_skill} on an integrated "
                    "(random-walk level) series — does not beat the naive last-value null; a level "
                    "R² is a mirage (report returns-based skill)"
                )
            elif skill > integrated_skill_bar:
                reasons.append(
                    f"persistence skill {skill:.3f} > {integrated_skill_bar} on a near-integrated "
                    "series — a random walk is near-unforecastable, so this is implausible "
                    "(likely leakage on levels)"
                )
        lag_corr = _corr(b[1:], a[:-1])
        if np.isfinite(lag_corr) and abs(lag_corr) > lag_corr_threshold:
            reasons.append(
                f"predictions correlate {lag_corr:.4f} with the lagged *actual* on a level series "
                "— level-lag fingerprint (ŷ_t ≈ y_(t-1))"
            )
    elif autocorrelated_stationary:
        # Overlapping / smoothed returns: persistence is an inappropriate null and
        # R² is inflated by the overlap. S5 abstains beyond the unconditional
        # backstop; de-overlapped evaluation / lookahead checks apply instead.
        pass
    else:
        # Low-autocorrelation returns: an honest forecast has tiny R².
        if np.isfinite(r2) and r2 > returns_r2_bar:
            reasons.append(
                f"R²={r2:.4f} exceeds the returns bar {returns_r2_bar} on a low-autocorrelation "
                "returns target — implausibly high for an honest returns forecast (leakage)"
            )

    return CheckResult("returns_not_levels", not reasons, reasons)


def check_horizon_monotonicity(
    error_by_horizon: dict[int, float], *, min_growth: float = 0.05
) -> CheckResult:
    """Flag a non-increasing OOS error-vs-horizon curve (S10) — a review flag.

    ``error_by_horizon`` maps horizon → OOS error (same metric across horizons).
    Flags: any decrease with horizon (inverted); or growth that is not
    *distributed* — fewer than half the steps grow meaningfully, or the end-to-end
    rise is below ``min_growth`` of the curve's scale (catches flat curves and
    curves that jump only at one endpoint, including the near-zero-short-horizon
    case a multiplicative endpoint test would auto-pass). Fail-closed on any
    non-finite or negative error.
    """
    if len(error_by_horizon) < 2:
        return CheckResult("horizon_monotonicity", False, ["need >= 2 horizons to test monotonicity"])

    horizons = sorted(error_by_horizon)
    errs = [float(error_by_horizon[h]) for h in horizons]
    if any((not np.isfinite(e)) or e < 0 for e in errs):
        return CheckResult(
            "horizon_monotonicity", False, ["non-finite or negative error value(s) — fail closed"]
        )

    reasons: list[str] = []

    for i in range(1, len(errs)):
        if errs[i] < errs[i - 1] * (1 - 1e-9):
            reasons.append(
                f"error decreases from horizon {horizons[i - 1]} ({errs[i - 1]:.4g}) to "
                f"{horizons[i]} ({errs[i]:.4g}) — inverted horizon curve (leakage fingerprint)"
            )
            break

    scale = max(errs) if max(errs) > 0 else 1.0
    steps = [errs[i] - errs[i - 1] for i in range(1, len(errs))]
    per_step_bar = min_growth * scale / len(steps)
    growing = sum(1 for s in steps if s > per_step_bar)
    end_to_end = errs[-1] - errs[0]
    if growing < len(steps) / 2 or end_to_end < min_growth * scale:
        reasons.append(
            f"error barely / unevenly grows with horizon ({horizons[0]}→{horizons[-1]}: "
            f"{errs[0]:.4g}→{errs[-1]:.4g}; {growing}/{len(steps)} steps grow) — a predictive "
            "model should degrade with horizon (leakage fingerprint, or an unpredictable series "
            "— review flag: adjudicate with a skill-vs-null check)"
        )

    return CheckResult("horizon_monotonicity", not reasons, reasons)
