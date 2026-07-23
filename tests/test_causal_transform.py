"""S7/S8 — non-causal transform leakage via check_causal_transform.

Bracket tests: each non-causal preprocessing transform (full-sample scaling,
full-sample detrend/decomposition, bidirectional smoothing) must FAIL, and its
causal (past-only) counterpart must PASS. These are the preprocessing-step leaks
that purge/embargo walk-forward misses — check_causal_transform audits the step
directly.
"""

import pytest

from project_money.validation import check_causal_transform
from tests.specimens import (
    FitOnceScaler,
    StatefulCountingTransform,
    centered_smooth_transform,
    column_dropping_transform,
    expanding_detrend_transform,
    expanding_minmax_transform,
    full_sample_detrend_transform,
    global_minmax_transform,
    string_output_transform,
    tail_fullsample_leak_transform,
    trailing_smooth_transform,
)


class TestCausalTransform:
    # S8 — scaling
    def test_global_minmax_scaling_caught(self, prices):
        result = check_causal_transform(global_minmax_transform, prices)
        assert not result.passed
        assert any("non-causal transform" in r for r in result.reasons)

    def test_expanding_minmax_passes(self, prices):
        assert check_causal_transform(expanding_minmax_transform, prices).passed

    # S7 — decomposition / detrend
    def test_full_sample_detrend_caught(self, prices):
        result = check_causal_transform(full_sample_detrend_transform, prices)
        assert not result.passed
        assert any("non-causal transform" in r for r in result.reasons)

    def test_expanding_detrend_passes(self, prices):
        assert check_causal_transform(expanding_detrend_transform, prices).passed

    # S8 — bidirectional smoothing / interpolation
    def test_centered_smoothing_caught(self, prices):
        assert not check_causal_transform(centered_smooth_transform, prices).passed

    def test_trailing_smoothing_passes(self, prices):
        assert check_causal_transform(trailing_smooth_transform, prices).passed

    def test_index_mismatch_fails_closed(self, prices):
        def reindexing_transform(data):
            return data.reset_index(drop=True)

        assert not check_causal_transform(reindexing_transform, prices).passed

    def test_deterministic_across_runs(self, prices):
        r1 = check_causal_transform(global_minmax_transform, prices)
        r2 = check_causal_transform(global_minmax_transform, prices)
        assert r1.passed == r2.passed and r1.reasons == r2.reasons


class TestCausalCoreRedTeamRegressions:
    """Findings from the shared-core red-team (harden check_no_lookahead too)."""

    def test_tail_full_sample_leak_caught(self, prices):
        # Finding 2: a leak in the untested tail — exhaustive cutoffs must catch it.
        result = check_causal_transform(tail_fullsample_leak_transform, prices)
        assert not result.passed
        assert any("non-causal transform" in r for r in result.reasons)

    def test_stateful_transform_diagnosed_distinctly(self, prices):
        # Finding 6: cross-call state → "stateful/nondeterministic", NOT "non-causal".
        result = check_causal_transform(StatefulCountingTransform(), prices)
        assert not result.passed
        assert any("stateful" in r or "nondeterministic" in r for r in result.reasons)
        assert not any("non-causal transform" in r for r in result.reasons)

    def test_non_numeric_output_fails_closed(self, prices):
        # Finding 7: fail closed, never crash.
        assert not check_causal_transform(string_output_transform, prices).passed

    def test_shape_change_fails_closed(self, prices):
        # Finding 8: a column drop under truncation fails closed, not a crash.
        result = check_causal_transform(column_dropping_transform, prices)
        assert not result.passed

    @pytest.mark.xfail(
        strict=True,
        reason="full-sample fit-once transform needs process/instance isolation — "
        "verification debt (core Finding 3, the ComputeOnce analogue)",
    )
    def test_fit_once_scaler_known_limitation(self, prices):
        assert not check_causal_transform(FitOnceScaler(), prices).passed
