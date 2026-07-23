"""S26 — calibration / process-fidelity axis (ECE)."""

import numpy as np

from project_money.validation import (
    check_calibration,
    expected_calibration_error,
    reliability_curve,
)
from tests.specimens import (
    confident_tail_miscalibration,
    high_abstention_forecast,
    overconfident_forecast,
    well_calibrated_forecast,
    within_bin_anticalibration,
)


class TestExpectedCalibrationError:
    def test_perfect_calibration_is_low(self):
        p, y = well_calibrated_forecast()
        assert expected_calibration_error(p, y) < 0.05

    def test_worst_case_is_one(self):
        # Always predict 1.0, outcome always 0 → ECE = 1.0.
        p = np.ones(200)
        y = np.zeros(200)
        assert abs(expected_calibration_error(p, y) - 1.0) < 1e-9

    def test_empty_is_nan(self):
        assert np.isnan(expected_calibration_error([], []))


class TestReliabilityCurve:
    def test_shape_and_counts(self):
        p, y = well_calibrated_forecast()
        curve = reliability_curve(p, y, n_bins=10)
        assert len(curve) == 10
        assert sum(row[4] for row in curve) == len(p)  # every sample binned once


class TestCheckCalibration:
    def test_well_calibrated_passes(self):
        p, y = well_calibrated_forecast()
        assert check_calibration(p, y).passed

    def test_overconfident_flagged(self):
        p, y = overconfident_forecast()
        result = check_calibration(p, y)
        assert not result.passed
        assert any("ECE" in r and "mandatory audit" in r for r in result.reasons)

    def test_probs_out_of_range_fail_closed(self):
        p = np.full(200, 1.5)
        y = (np.arange(200) % 2).astype(float)
        assert not check_calibration(p, y).passed

    def test_non_binary_outcomes_fail_closed(self):
        p = np.full(200, 0.5)
        y = np.full(200, 0.7)  # not 0/1
        assert not check_calibration(p, y).passed

    def test_length_mismatch_fails_closed(self):
        assert not check_calibration(np.full(200, 0.5), np.zeros(199)).passed

    def test_insufficient_samples_fail_closed(self):
        p = np.full(10, 0.5)
        y = (np.arange(10) % 2).astype(float)
        assert not check_calibration(p, y, min_samples=50).passed

    def test_deterministic_across_runs(self):
        p, y = overconfident_forecast()
        r1, r2 = check_calibration(p, y), check_calibration(p, y)
        assert r1.passed == r2.passed and r1.reasons == r2.reasons

    # --- red-team regressions ---

    def test_perfect_forecaster_small_n_not_false_flagged(self):
        # Finding 1: at small N the bootstrap null band must not reject a perfect
        # forecaster (the fixed 0.1 bar did ~89% of the time at N=50).
        p, y = well_calibrated_forecast(n_obs=60)
        assert check_calibration(p, y).passed

    def test_confident_tail_flagged_by_mce(self):
        # Finding 2: ~9% maximally-confident-wrong tail — count-weighted ECE forgives
        # it, MCE-with-count-floor must catch it.
        p, y = confident_tail_miscalibration()
        result = check_calibration(p, y)
        assert not result.passed
        assert any("MCE" in r for r in result.reasons)

    def test_within_bin_anticalibration_flagged(self):
        # Finding 3: anti-calibration hidden within a wide bin — the finer-binning
        # pass must surface it.
        p, y = within_bin_anticalibration()
        assert not check_calibration(p, y).passed

    def test_high_abstention_flagged_by_coverage(self):
        # Finding 4: abstaining (NaN) on most cases must be flagged by the coverage floor.
        p, y = high_abstention_forecast()
        result = check_calibration(p, y)
        assert not result.passed
        assert any("coverage" in r for r in result.reasons)
