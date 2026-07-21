import math

import numpy as np
import pandas as pd
import pytest

from project_money.validation.metrics import (
    compute_metrics,
    deflated_sharpe,
    portfolio_returns,
)
from tests.conftest import causal_momentum_signal


class TestPortfolioReturns:
    def test_deterministic(self, prices, returns):
        w = causal_momentum_signal(prices)
        a = portfolio_returns(w, returns)
        b = portfolio_returns(w, returns)
        pd.testing.assert_series_equal(a, b)

    def test_costs_reduce_pnl(self, prices, returns):
        w = causal_momentum_signal(prices)
        gross = portfolio_returns(w, returns, cost_bps=0.0)
        net = portfolio_returns(w, returns, cost_bps=10.0)
        assert net.sum() < gross.sum()

    def test_one_bar_delay(self, returns):
        """Weights set on day t earn day t+1's return, never day t's — a
        same-bar-execution leak would show up as day-t attribution."""
        w = pd.DataFrame(0.0, index=returns.index, columns=returns.columns)
        t = returns.index[100]
        w.loc[t, returns.columns[0]] = 1.0
        pnl = portfolio_returns(w, returns)
        assert pnl.loc[t] == 0.0
        t_next = returns.index[101]
        assert pnl.loc[t_next] == pytest.approx(returns.loc[t_next, returns.columns[0]])


class TestComputeMetrics:
    def test_expected_keys(self, prices, returns):
        m = compute_metrics(causal_momentum_signal(prices), returns)
        for key in (
            "sharpe_net",
            "sharpe_gross",
            "max_drawdown",
            "avg_turnover",
            "cagr",
            "hit_rate",
        ):
            assert key in m

    def test_gross_geq_net_with_costs(self, prices, returns):
        m = compute_metrics(causal_momentum_signal(prices), returns, cost_bps=10.0)
        assert m["sharpe_gross"] >= m["sharpe_net"]

    def test_drawdown_nonpositive(self, prices, returns):
        m = compute_metrics(causal_momentum_signal(prices), returns)
        assert m["max_drawdown"] <= 0.0

    def test_empty_raises(self, prices):
        with pytest.raises(ValueError):
            compute_metrics(causal_momentum_signal(prices), prices.pct_change().iloc[:0])


class TestDeflatedSharpe:
    def test_monotone_decreasing_in_trials(self):
        probs = [deflated_sharpe(1.0, n, 252 * 3) for n in (1, 10, 100, 1000)]
        assert all(a >= b for a, b in zip(probs, probs[1:]))

    def test_single_trial_matches_plain_psr(self):
        """With one trial, DSR reduces to the Probabilistic Sharpe Ratio,
        including its skew/kurtosis denominator (Bailey & Lopez de Prado):
        z = SR sqrt(n-1) / sqrt(1 - g3*SR + (g4-1)/4 * SR^2), g3=0, g4=3."""
        p = deflated_sharpe(1.0, 1, 252 * 3)
        sr = 1.0 / math.sqrt(252)
        denom = math.sqrt(1.0 + 0.5 * sr**2)
        from statistics import NormalDist

        expected = NormalDist().cdf(sr * math.sqrt(252 * 3 - 1) / denom)
        assert p == pytest.approx(expected, abs=1e-9)

    def test_many_trials_deflate_a_modest_sharpe(self):
        """A 0.8 Sharpe found after 500 trials on 2y of data should NOT be
        confidently positive — this is the anti-p-hacking property."""
        p = deflated_sharpe(0.8, 500, 252 * 2)
        assert p < 0.95

    def test_input_validation(self):
        with pytest.raises(ValueError):
            deflated_sharpe(1.0, 0, 252)
        with pytest.raises(ValueError):
            deflated_sharpe(1.0, 10, 1)


class TestDeflatedSharpeBatch3Corrections:
    """Regression tests for the batch-3 verified corrections (de Prado):
    the benchmark must scale with cross-trial SR variance, and the formula
    takes RAW kurtosis."""

    def test_excess_kurtosis_rejected_with_hint(self):
        with pytest.raises(ValueError, match="excess"):
            deflated_sharpe(1.0, 10, 504, kurtosis=0.0)  # Gaussian EXCESS kurt

    def test_kurtosis_raw_key_matches_convention(self, prices, returns):
        from project_money.validation.metrics import compute_metrics
        from tests.conftest import causal_momentum_signal

        m = compute_metrics(causal_momentum_signal(prices), returns)
        assert m["kurtosis_raw"] == pytest.approx(m["kurtosis"] + 3.0)
        # raw kurtosis is mathematically >= 1
        assert m["kurtosis_raw"] >= 1.0

    def test_diverse_trials_raise_the_bar(self):
        """Empirical cross-trial variance > IID-null approximation ⇒ the
        corrected DSR must be LOWER (the old default was anti-conservative)."""
        diverse = [-1.5, -0.5, 0.3, 0.9, 1.8, 2.4]  # widely dispersed trial SRs
        p_default = deflated_sharpe(1.5, 6, 504)
        p_corrected = deflated_sharpe(1.5, 6, 504, trial_sharpes=diverse)
        assert p_corrected < p_default

    def test_near_clone_trials_lower_the_bar(self):
        """Near-identical trials ⇒ tiny cross-trial variance ⇒ corrected DSR
        HIGHER than the IID-null fallback (old default over-conservative)."""
        clones = [1.49, 1.50, 1.51, 1.50, 1.495, 1.505]
        p_default = deflated_sharpe(1.5, 6, 504)
        p_corrected = deflated_sharpe(1.5, 6, 504, trial_sharpes=clones)
        assert p_corrected > p_default

    def test_single_trial_unaffected(self):
        """n_trials=1 has no benchmark — trial_sharpes must not change PSR."""
        a = deflated_sharpe(1.0, 1, 756)
        b = deflated_sharpe(1.0, 1, 756, trial_sharpes=[1.0])
        assert a == b


class TestLedgerSharpeWiring:
    def test_recorded_sharpes_feed_the_corrected_dsr(self, tmp_path):
        from project_money.ledger import HypothesisLedger, LedgerEntry

        led = HypothesisLedger(tmp_path / "l.jsonl")
        for i, sr in enumerate([0.4, 1.1, -0.2, 0.8]):
            led.append(
                LedgerEntry(
                    entry_id=f"h{i}",
                    ts="2026-07-21T00:00:00",
                    family="momentum",
                    hypothesis=f"variant {i}",
                    status="validation_pending",
                    scores={"sharpe_net": sr},
                )
            )
        srs = led.recorded_sharpes("momentum")
        assert sorted(srs) == [-0.2, 0.4, 0.8, 1.1]
        p = deflated_sharpe(1.1, led.n_trials("momentum"), 504, trial_sharpes=srs)
        assert 0.0 < p < 1.0

    def test_recorded_sharpes_skips_missing_scores(self, tmp_path):
        from project_money.ledger import HypothesisLedger, LedgerEntry

        led = HypothesisLedger(tmp_path / "l.jsonl")
        led.append(
            LedgerEntry(
                entry_id="h1",
                ts="2026-07-21T00:00:00",
                family="momentum",
                hypothesis="no score yet",
                status="proposed",
            )
        )
        assert led.recorded_sharpes() == []
