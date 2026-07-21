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
