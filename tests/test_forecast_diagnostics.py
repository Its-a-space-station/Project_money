"""S5 (returns-not-levels via persistence null) and S10 (horizon monotonicity).

Bracket tests targeting the Nabipour specimen plus the red-team regressions:
threshold-window dodge, is_levels-flip dodge, AR/momentum false-positive guard,
near-zero and endpoint-jump horizon curves, and fail-closed hygiene.
"""

import numpy as np

from project_money.validation import check_horizon_monotonicity, check_returns_not_levels
from tests.specimens import (
    ar_momentum_returns_forecast,
    contemporaneous_returns_leak,
    growing_horizon_errors,
    honest_returns_forecast,
    level_forecast_threshold_dodge,
    nabipour_horizon_errors,
    nabipour_level_forecast,
    overlapping_returns_honest_forecast,
    returns_contemporaneous_leak_moderate,
    trending_level_plausible_leak,
)


class TestReturnsNotLevels:
    def test_nabipour_level_forecast_flagged(self):
        y_true, y_pred = nabipour_level_forecast()
        result = check_returns_not_levels(y_true, y_pred, is_levels=True)
        assert not result.passed

    def test_honest_returns_forecast_passes(self):
        y_true, y_pred = honest_returns_forecast()
        assert check_returns_not_levels(y_true, y_pred, is_levels=False).passed

    def test_level_lag_persistence_flagged(self):
        y_true, _ = nabipour_level_forecast()
        y_pred = y_true.shift(1).bfill()
        result = check_returns_not_levels(y_true, y_pred, is_levels=True)
        assert not result.passed

    # --- red-team regressions ---

    def test_threshold_window_dodge_caught(self):
        # #1: near-perfect level fit degraded past R²=0.95; persistence skill << 0.
        y_true, y_pred = level_forecast_threshold_dodge()
        result = check_returns_not_levels(y_true, y_pred, is_levels=True)
        assert not result.passed
        assert any("persistence skill" in r for r in result.reasons)

    def test_level_ness_is_inferred_not_trusted(self):
        # #1: even with NO is_levels hint, a level series is inferred and the dodge caught.
        y_true, y_pred = level_forecast_threshold_dodge()
        assert not check_returns_not_levels(y_true, y_pred).passed

    def test_contemporaneous_returns_leak_caught_despite_is_levels_false(self):
        # #2: R²≈1 flagged unconditionally, even when is_levels=False is claimed.
        y_true, y_pred = contemporaneous_returns_leak()
        result = check_returns_not_levels(y_true, y_pred, is_levels=False)
        assert not result.passed
        assert any("R²" in r for r in result.reasons)

    def test_ar_momentum_returns_not_false_flagged(self):
        # #5: a legitimate AR/momentum returns forecast must PASS (not level-lag).
        y_true, y_pred = ar_momentum_returns_forecast()
        assert check_returns_not_levels(y_true, y_pred).passed
        assert check_returns_not_levels(y_true, y_pred, is_levels=False).passed

    def test_insufficient_sample_fails_closed(self):
        assert not check_returns_not_levels([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]).passed

    # --- round-2 regressions ---

    def test_moderate_r2_returns_leak_caught(self):
        # #1: a returns leak at R²≈0.9 (below the 0.99 bar) — the regime-aware
        # returns R² bar must catch it, inferred or with is_levels=False.
        y_true, y_pred = returns_contemporaneous_leak_moderate()
        assert not check_returns_not_levels(y_true, y_pred).passed
        assert not check_returns_not_levels(y_true, y_pred, is_levels=False).passed

    def test_overlapping_returns_not_false_flagged(self):
        # #2: honest overlapping k-day return forecast must PASS (abstain regime).
        y_true, y_pred = overlapping_returns_honest_forecast()
        assert check_returns_not_levels(y_true, y_pred).passed

    def test_trending_level_plausible_leak_caught(self):
        # #3: a contemporaneous leak on a random-walk level must be caught by the
        # integrated regime.
        y_true, y_pred = trending_level_plausible_leak()
        assert not check_returns_not_levels(y_true, y_pred, is_levels=True).passed


class TestHorizonMonotonicity:
    def test_flat_horizon_curve_flagged(self):
        result = check_horizon_monotonicity(nabipour_horizon_errors())
        assert not result.passed

    def test_growing_error_curve_passes(self):
        assert check_horizon_monotonicity(growing_horizon_errors()).passed

    def test_inverted_curve_flagged(self):
        result = check_horizon_monotonicity({1: 2.0, 5: 1.5, 10: 1.0})
        assert not result.passed
        assert any("inverted" in r for r in result.reasons)

    def test_near_zero_short_horizon_curve_flagged(self):
        # #3: multiplicative baseline collapses at ~0; the loudest leak signature
        # must NOT auto-pass.
        result = check_horizon_monotonicity({1: 1e-12, 5: 1e-12, 10: 1e-12, 20: 1e-12, 30: 1e-4})
        assert not result.passed

    def test_endpoint_only_jump_flagged(self):
        # #4: flat across 80% of horizons with a single end jump must be caught.
        result = check_horizon_monotonicity({1: 0.010, 5: 0.010, 10: 0.010, 20: 0.010, 30: 0.0106})
        assert not result.passed

    def test_non_finite_error_fails_closed(self):
        # #10: NaN errors must fail closed like negatives do.
        assert not check_horizon_monotonicity({1: 0.01, 5: 0.01, 30: float("nan")}).passed

    def test_single_horizon_fails_closed(self):
        assert not check_horizon_monotonicity({1: 0.5}).passed
