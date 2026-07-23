import numpy as np
import pandas as pd
import pytest

from project_money.validation import (
    check_data_integrity,
    check_no_lookahead,
    check_weights_valid,
)
from tests.conftest import causal_momentum_signal, lookahead_signal
from tests.specimens import grid_gamed_lookahead_signal


class TestDataIntegrity:
    def test_clean_panel_passes(self, prices):
        result = check_data_integrity(prices)
        assert result.passed, result.reasons

    def test_duplicate_timestamps_fail(self, prices):
        bad = pd.concat([prices, prices.iloc[[10]]]).sort_index()
        result = check_data_integrity(bad)
        assert not result.passed
        assert any("duplicate" in r for r in result.reasons)

    def test_non_monotonic_fails(self, prices):
        bad = prices.iloc[::-1]
        assert not check_data_integrity(bad).passed

    def test_negative_prices_fail(self, prices):
        bad = prices.copy()
        bad.iloc[5, 0] = -1.0
        result = check_data_integrity(bad)
        assert not result.passed
        assert any("non-positive" in r for r in result.reasons)

    def test_excessive_nans_fail(self, prices):
        bad = prices.copy()
        bad.iloc[: len(bad) // 2, 1] = np.nan
        result = check_data_integrity(bad)
        assert not result.passed
        assert any("NaN fraction" in r for r in result.reasons)

    def test_extreme_returns_flagged(self, prices):
        bad = prices.copy()
        bad.iloc[100, 2] = bad.iloc[99, 2] * 3.0  # +200% bar
        result = check_data_integrity(bad)
        assert not result.passed
        assert any("needs_human_review" in r for r in result.reasons)


class TestWeightsValid:
    def test_valid_weights_pass(self, prices):
        w = causal_momentum_signal(prices)
        assert check_weights_valid(w).passed

    def test_gross_exposure_cap(self, prices):
        w = causal_momentum_signal(prices) * 3.0
        result = check_weights_valid(w)
        assert not result.passed
        assert any("gross exposure" in r for r in result.reasons)

    def test_shorts_rejected_by_default(self, prices):
        w = causal_momentum_signal(prices)
        w.iloc[50, 0] = -0.1
        assert not check_weights_valid(w).passed
        assert check_weights_valid(w, allow_short=True, max_gross=2.0).passed

    def test_nonfinite_rejected(self, prices):
        w = causal_momentum_signal(prices)
        w.iloc[10, 1] = np.inf
        assert not check_weights_valid(w).passed


class TestNoLookahead:
    """The bracket test for our own lookahead detector: it must PASS the
    causal signal and FAIL the contaminated one (fail-before / pass-after)."""

    def test_causal_signal_passes(self, prices):
        result = check_no_lookahead(causal_momentum_signal, prices)
        assert result.passed, result.reasons

    def test_lookahead_signal_caught(self, prices):
        result = check_no_lookahead(lookahead_signal, prices)
        assert not result.passed
        assert any("lookahead" in r for r in result.reasons)

    def test_full_sample_normalization_caught(self, prices):
        """A subtler leak: z-scoring by the full-sample mean/std."""

        def zscore_leak(p: pd.DataFrame) -> pd.DataFrame:
            rets = p.pct_change()
            z = (rets - rets.mean()) / rets.std()  # full-sample moments — leak
            w = (z > 0).astype(float)
            gross = w.sum(axis=1).replace(0, np.nan)
            return w.div(gross, axis=0).fillna(0.0)

        assert not check_no_lookahead(zscore_leak, prices).passed

    def test_insufficient_history_flagged(self, prices):
        result = check_no_lookahead(causal_momentum_signal, prices.iloc[:10], min_history=30)
        assert not result.passed

    def test_grid_gamed_lookahead_caught(self, prices):
        # Core red-team Finding 1 (CRITICAL): a 1-day lookahead that zeroes itself on
        # the old evenly-spaced cutoff grid. Exhaustive cutoffs must still catch it.
        result = check_no_lookahead(grid_gamed_lookahead_signal, prices)
        assert not result.passed
        assert any("lookahead" in r for r in result.reasons)
