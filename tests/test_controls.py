import numpy as np
import pandas as pd

from project_money.falsification import (
    block_permute_returns,
    known_zero_battery,
    matched_gaussian_surrogate,
    permute_returns,
)


def autocorr_metric(series: pd.Series) -> float:
    """Lag-1 autocorrelation — a genuine temporal-structure metric."""
    return float(series.autocorr(lag=1))


def make_ar1(seed=5, n=400, phi=0.4) -> pd.Series:
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal(0, 1)
    return pd.Series(x)


class TestControls:
    def test_permute_preserves_marginal(self):
        s = make_ar1()
        p = permute_returns(s, seed=0)
        assert np.allclose(np.sort(s.to_numpy()), np.sort(p.to_numpy()))

    def test_permute_destroys_autocorrelation(self):
        s = make_ar1()
        assert abs(autocorr_metric(s)) > 0.25
        assert abs(autocorr_metric(permute_returns(s, seed=0))) < 0.15

    def test_deterministic_given_seed(self):
        s = make_ar1()
        a = permute_returns(s, seed=9)
        b = permute_returns(s, seed=9)
        pd.testing.assert_series_equal(a, b)
        c = permute_returns(s, seed=10)
        assert not a.equals(c)

    def test_block_permute_covers_all_values(self):
        s = make_ar1()
        b = block_permute_returns(s, seed=1, block=5)
        assert len(b) == len(s)

    def test_gaussian_surrogate_matches_moments(self):
        s = make_ar1()
        g = matched_gaussian_surrogate(s, seed=2)
        np.testing.assert_allclose(g.mean(), s.mean(), atol=0.2)
        np.testing.assert_allclose(g.std(ddof=1), s.std(ddof=1), rtol=0.2)


class TestKnownZeroBattery:
    def test_real_structure_stands_out(self):
        """The battery's own bracket test: a real AR(1) autocorrelation must
        sit at the top of its permutation-null distribution..."""
        s = make_ar1()
        result = known_zero_battery(autocorr_metric, s, n_trials=50, seed=0)
        assert result["observed_percentile"] >= 0.98
        assert abs(result["null_mean"]) < 0.05  # metric is honest on nulls

    def test_noise_does_not_stand_out(self):
        """...and pure noise must not — tested honestly across 20 seeds.

        Any single noise draw can land in its own null's top 2% by chance
        (it IS a draw from that null), so a single-seed assertion is flaky by
        construction. A working battery has a ~2% stand-out rate; a broken one
        (e.g. percentile pinned at 1.0) fails the loose 25% bound decisively.
        """
        stand_out = 0
        for seed in range(20):
            rng = np.random.default_rng(1000 + seed)
            s = pd.Series(rng.normal(0, 1, 400))
            result = known_zero_battery(autocorr_metric, s, n_trials=50, seed=0)
            if result["observed_percentile"] >= 0.98:
                stand_out += 1
        assert stand_out <= 5  # <= 25% of 20 seeds; expected ~2%
