"""V5 — macro/micro dual aggregation (prevalence-skew guard).

A pooled (micro) edge must be corroborated per pre-registered regime. A
majority-regime specialist → needs_human_review (may be a real conditional edge);
too little of the data judgeable → validation_pending; malformed input → reject;
no pooled edge → pass (nothing to distrust).
"""

import numpy as np
import pytest

from project_money.validation import Stage, check_regime_robustness, run_cascade


def _mean_check(values, regimes, **kw):
    return check_regime_robustness(values, regimes, metric_fn=np.mean, bar=0.0, **kw)


class TestRegimeRobustness:
    def test_robust_edge_passes(self):
        values = np.full(150, 1.0)
        regimes = ["a"] * 50 + ["b"] * 50 + ["c"] * 50
        assert _mean_check(values, regimes).passed

    def test_prevalence_skew_is_needs_human_review(self):
        # Pooled mean > 0 (carried by the large regime) but regime 'b' is negative.
        values = np.concatenate([np.full(100, 1.0), np.full(40, -0.5)])
        regimes = ["a"] * 100 + ["b"] * 40
        r = _mean_check(values, regimes)
        assert not r.passed and r.disposition == "needs_human_review"
        assert any("prevalence skew" in x for x in r.reasons)

    def test_no_pooled_edge_passes(self):
        # Nothing to distrust when the pooled metric does not clear the bar.
        values = np.full(60, -1.0)
        regimes = ["a"] * 30 + ["b"] * 30
        assert _mean_check(values, regimes).passed

    def test_low_coverage_is_validation_pending(self):
        # Pooled clears, the one big regime clears, but 40/140 obs are in un-judgeable
        # tiny regimes → robustness unverifiable for the rest.
        values = np.concatenate([np.full(100, 1.0), np.full(40, 1.0)])
        regimes = ["big"] * 100 + [f"t{i // 2}" for i in range(40)]
        r = _mean_check(values, regimes)
        assert not r.passed and r.disposition == "validation_pending"
        assert any("robustness unverifiable" in x for x in r.reasons)

    def test_lower_is_better_skew(self):
        # An error metric: pooled error clears (<= bar) but a regime's error does not.
        values = np.concatenate([np.full(300, 0.02), np.full(40, 0.5)])
        regimes = ["a"] * 300 + ["b"] * 40
        r = check_regime_robustness(values, regimes, metric_fn=np.mean, bar=0.1, higher_is_better=False)
        assert not r.passed and r.disposition == "needs_human_review"

    def test_length_mismatch_fails_closed(self):
        assert not check_regime_robustness(
            np.full(20, 1.0), ["a"] * 19, metric_fn=np.mean, bar=0.0
        ).passed

    def test_insufficient_sample_fails_closed(self):
        assert not _mean_check(np.full(10, 1.0), ["a"] * 10).passed

    def test_non_finite_pooled_metric_fails_closed(self):
        r = check_regime_robustness(
            np.full(40, 1.0), ["a"] * 20 + ["b"] * 20, metric_fn=lambda a: float("nan"), bar=0.0
        )
        assert not r.passed and r.disposition == "reject"

    def test_nan_values_dropped_then_judged(self):
        values = np.concatenate([np.full(100, 1.0), np.full(40, -0.5), np.full(5, np.nan)])
        regimes = ["a"] * 100 + ["b"] * 40 + ["a"] * 5
        r = _mean_check(values, regimes)
        assert not r.passed and r.disposition == "needs_human_review"  # NaNs dropped, skew still caught

    # --- red-team regressions (skeptic V5 round) ---

    def test_non_finite_bar_fails_closed(self):
        # A non-finite bar made clears() always False → the "nothing to distrust" PASS
        # waved a non-robust strategy through. Must fail closed (reject).
        values = np.concatenate([np.full(100, 1.0), np.full(40, -5.0)])
        regimes = ["a"] * 100 + ["b"] * 40
        for bad_bar in (float("nan"), float("inf"), float("-inf")):
            r = check_regime_robustness(values, regimes, metric_fn=np.mean, bar=bad_bar)
            assert not r.passed and r.disposition == "reject", bad_bar

    def test_min_coverage_zero_or_out_of_range_fails_closed(self):
        values = np.full(60, 1.0)
        regimes = ["a"] * 30 + ["b"] * 30
        for bad in (0.0, -0.1, 1.5, float("nan")):
            r = check_regime_robustness(values, regimes, metric_fn=np.mean, bar=0.0, min_coverage=bad)
            assert not r.passed and r.disposition == "reject", bad

    def test_min_regime_n_nonpositive_fails_closed(self):
        values = np.full(60, 1.0)
        regimes = ["a"] * 30 + ["b"] * 30
        for bad in (0, -5):
            r = check_regime_robustness(values, regimes, metric_fn=np.mean, bar=0.0, min_regime_n=bad)
            assert not r.passed and r.disposition == "reject", bad

    def test_inf_values_dropped(self):
        # +inf in values is dropped like NaN (np.isfinite), not propagated into a regime metric.
        values = np.concatenate([np.full(100, 1.0), np.full(40, -0.5), np.full(3, np.inf)])
        regimes = ["a"] * 100 + ["b"] * 40 + ["a"] * 3
        r = _mean_check(values, regimes)
        assert not r.passed and r.disposition == "needs_human_review"  # inf dropped, skew still caught


class TestRegimeRobustnessInCascade:
    def test_robust_promotes(self):
        values = np.full(90, 1.0)
        regimes = ["a"] * 45 + ["b"] * 45
        stage = Stage.from_check("v5", lambda c: _mean_check(values, regimes))
        assert run_cascade("cand", [stage]).label == "trigger_ready_research_candidate"

    def test_skew_is_needs_human_review(self):
        values = np.concatenate([np.full(100, 1.0), np.full(40, -0.5)])
        regimes = ["a"] * 100 + ["b"] * 40
        stage = Stage.from_check("v5", lambda c: _mean_check(values, regimes))
        assert run_cascade("cand", [stage]).label == "needs_human_review"

    def test_low_coverage_is_validation_pending(self):
        values = np.concatenate([np.full(100, 1.0), np.full(40, 1.0)])
        regimes = ["big"] * 100 + [f"t{i // 2}" for i in range(40)]
        stage = Stage.from_check("v5", lambda c: _mean_check(values, regimes))
        assert run_cascade("cand", [stage]).label == "validation_pending"
