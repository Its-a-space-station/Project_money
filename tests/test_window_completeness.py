"""V1 — window-completeness assertion (anti-drop-last).

Bracket test: PASS a fully-scored sliding-window evaluation; FAIL the drop-last
fingerprint (fewer windows than the declared geometry implies) and any count that
moves with an engineering-only parameter. Plus fail-closed guards on malformed
inputs, degenerate zero-window geometries, and internally inconsistent
declarations.
"""

import numpy as np
import pytest

from project_money.validation import check_window_completeness, expected_window_count


class TestExpectedWindowCount:
    @pytest.mark.parametrize(
        "n_obs, lookback, horizon, stride, expected",
        [
            (100, 10, 1, 1, 90),  # p in 0..89
            (100, 10, 1, 5, 18),  # floor(89/5)+1
            (11, 10, 1, 1, 1),  # exactly one window fits
            (10, 10, 1, 1, 0),  # span 11 > n_obs 10 → none
            (50, 0, 1, 1, 50),  # zero lookback, span == horizon
            (5, 3, 2, 1, 1),  # span == n_obs
        ],
    )
    def test_formula(self, n_obs, lookback, horizon, stride, expected):
        assert expected_window_count(n_obs, lookback, horizon, stride) == expected


class TestWindowCompleteness:
    def test_fully_scored_geometry_passes(self):
        r = check_window_completeness(90, n_obs=100, lookback=10, horizon=1, stride=1)
        assert r.passed, r.reasons

    def test_drop_last_caught(self):
        # batch_size=32 over 90 windows keeps 2 full batches (64), drops the last 26.
        r = check_window_completeness(64, n_obs=100, lookback=10, horizon=1, stride=1)
        assert not r.passed
        assert r.disposition == "reject"
        assert any("drop-last" in reason for reason in r.reasons)

    def test_excess_windows_caught(self):
        r = check_window_completeness(95, n_obs=100, lookback=10, horizon=1, stride=1)
        assert not r.passed
        assert any("extra" in reason for reason in r.reasons)

    def test_explicit_expected_passes(self):
        r = check_window_completeness(90, expected_windows=90)
        assert r.passed, r.reasons

    def test_explicit_expected_mismatch_caught(self):
        r = check_window_completeness(64, expected_windows=90)
        assert not r.passed
        assert any("drop-last" in reason for reason in r.reasons)

    def test_geometry_and_explicit_agree_passes(self):
        r = check_window_completeness(
            90, expected_windows=90, n_obs=100, lookback=10, horizon=1, stride=1
        )
        assert r.passed, r.reasons

    def test_geometry_and_explicit_disagree_fails_closed(self):
        # A declared count that contradicts the declared geometry is inconsistent.
        r = check_window_completeness(
            90, expected_windows=90, n_obs=100, lookback=10, horizon=5, stride=1
        )
        assert not r.passed
        assert any("inconsistent declaration" in reason for reason in r.reasons)

    def test_engineering_variance_caught(self):
        # drop_last=False scores 90; drop_last=True (batch 32) scores 64 → not invariant.
        r = check_window_completeness(
            90,
            n_obs=100,
            lookback=10,
            horizon=1,
            stride=1,
            engineering_counts={"drop_last=True,batch=32": 64},
        )
        assert not r.passed
        assert any("engineering parameter" in reason for reason in r.reasons)

    def test_engineering_counts_all_equal_passes(self):
        r = check_window_completeness(
            90,
            n_obs=100,
            lookback=10,
            horizon=1,
            stride=1,
            engineering_counts={"batch=16": 90, "batch=32": 90, "chunk=64": 90},
        )
        assert r.passed, r.reasons

    # --- fail-closed guards ---

    def test_zero_window_geometry_fails_closed(self):
        # span (10+1) > n_obs (5): the evaluation could not score a single window.
        r = check_window_completeness(0, n_obs=5, lookback=10, horizon=1)
        assert not r.passed
        assert any("zero scored windows" in reason for reason in r.reasons)

    def test_partial_geometry_fails_closed(self):
        r = check_window_completeness(90, n_obs=100, lookback=10)  # no horizon
        assert not r.passed
        assert any("all be given together" in reason for reason in r.reasons)

    def test_neither_expected_nor_geometry_fails_closed(self):
        r = check_window_completeness(90)
        assert not r.passed
        assert any("must supply either" in reason for reason in r.reasons)

    def test_bool_count_fails_closed(self):
        # bool is an int subclass — must not be silently accepted as a count.
        r = check_window_completeness(True, expected_windows=1)
        assert not r.passed
        assert any("scored_windows" in reason for reason in r.reasons)

    def test_negative_count_fails_closed(self):
        r = check_window_completeness(-1, expected_windows=90)
        assert not r.passed

    def test_float_count_fails_closed(self):
        r = check_window_completeness(90.0, expected_windows=90)
        assert not r.passed
        assert any("fail closed" in reason for reason in r.reasons)

    def test_bad_stride_fails_closed(self):
        r = check_window_completeness(90, n_obs=100, lookback=10, horizon=1, stride=0)
        assert not r.passed
        assert any("stride" in reason for reason in r.reasons)

    def test_engineering_counts_non_mapping_fails_closed(self):
        r = check_window_completeness(90, expected_windows=90, engineering_counts=[90, 90])
        assert not r.passed
        assert any("must be a mapping" in reason for reason in r.reasons)

    def test_bad_engineering_count_value_fails_closed(self):
        r = check_window_completeness(
            90, expected_windows=90, engineering_counts={"batch=32": 90.0}
        )
        assert not r.passed

    def test_numpy_int_count_accepted(self):
        r = check_window_completeness(np.int64(90), expected_windows=90)
        assert r.passed, r.reasons

    def test_deterministic_across_runs(self):
        r1 = check_window_completeness(64, n_obs=100, lookback=10, horizon=1)
        r2 = check_window_completeness(64, n_obs=100, lookback=10, horizon=1)
        assert r1.passed == r2.passed and r1.reasons == r2.reasons

    # --- red-team regressions (research-skeptic round 1) ---

    def test_engineering_count_str_collision_not_masked(self):
        # Finding 3: labels 32 (int) and "32" (str) share a str(); the violating
        # count of 64 must NOT be silently dropped, in EITHER dict order.
        r1 = check_window_completeness(
            90, n_obs=100, lookback=10, horizon=1, engineering_counts={32: 64, "32": 90}
        )
        r2 = check_window_completeness(
            90, n_obs=100, lookback=10, horizon=1, engineering_counts={"32": 90, 32: 64}
        )
        assert not r1.passed and not r2.passed
        assert r1.passed == r2.passed  # outcome is not dict-order dependent
        assert any("engineering parameter" in reason for reason in r1.reasons)

    def test_stride_validated_without_geometry(self):
        # Finding 4: stride is the gate's own knob — an out-of-range value must
        # reject even when no geometry consumes it.
        r = check_window_completeness(90, expected_windows=90, stride=-5)
        assert not r.passed
        assert any("stride" in reason for reason in r.reasons)

    def test_zero_stride_without_geometry_fails_closed(self):
        # A stride=0 with no geometry must fail closed, never reach a // by zero.
        r = check_window_completeness(90, expected_windows=90, stride=0)
        assert not r.passed
        assert any("stride" in reason for reason in r.reasons)
