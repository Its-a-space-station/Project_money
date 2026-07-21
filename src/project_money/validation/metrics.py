"""Multi-metric evaluation recomputed from raw artifacts.

Doctrine (synthesis §3.1, §4 tool 1): metrics are recomputed from the primitive
artifacts — weights and returns — never accepted from a generating agent's
report; the result is a *dict of metrics*, never a single scalar (AlphaEvolve).
``deflated_sharpe`` implements the multiplicity correction that the hypothesis
ledger's trial counts feed (Bailey & Lopez de Prado 2014).

Research-only: simulated allocations under study; nothing here is a directive.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def portfolio_returns(
    weights: pd.DataFrame,
    asset_returns: pd.DataFrame,
    *,
    cost_bps: float = 0.0,
) -> pd.Series:
    """Deterministic simulated portfolio returns from a weight panel.

    Weights are applied with a one-bar delay (no same-bar execution — a
    structural no-lookahead guard), and linear costs of ``cost_bps`` basis
    points are charged on turnover.
    """
    w = weights.reindex(asset_returns.index).shift(1).fillna(0.0)
    gross = (w * asset_returns.fillna(0.0)).sum(axis=1)
    turnover = w.diff().abs().sum(axis=1).fillna(0.0)
    costs = turnover * (cost_bps / 1e4)
    return gross - costs


def compute_metrics(
    weights: pd.DataFrame,
    asset_returns: pd.DataFrame,
    *,
    cost_bps: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> dict[str, float]:
    """Recompute the standard multi-metric dict from artifacts.

    Returns a plain dict so cascade stages, niches, and reports can consume it
    without any custom types. Keys are stable API.
    """
    pnl = portfolio_returns(weights, asset_returns, cost_bps=cost_bps)
    pnl_gross = portfolio_returns(weights, asset_returns, cost_bps=0.0)
    n = len(pnl)
    if n == 0:
        raise ValueError("empty return series")

    ann = periods_per_year
    mean, std = float(pnl.mean()), float(pnl.std(ddof=1))
    mean_g, std_g = float(pnl_gross.mean()), float(pnl_gross.std(ddof=1))

    equity = (1.0 + pnl).cumprod()
    peak = equity.cummax()
    drawdown = equity / peak - 1.0

    w = weights.reindex(asset_returns.index).shift(1).fillna(0.0)
    turnover = w.diff().abs().sum(axis=1).fillna(0.0)

    years = n / ann
    total_return = float(equity.iloc[-1] - 1.0)
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 and equity.iloc[-1] > 0 else float("nan")

    return {
        "n_periods": float(n),
        "total_return": total_return,
        "cagr": cagr,
        "ann_vol": std * math.sqrt(ann),
        "sharpe_net": (mean / std) * math.sqrt(ann) if std > 0 else float("nan"),
        "sharpe_gross": (mean_g / std_g) * math.sqrt(ann) if std_g > 0 else float("nan"),
        "max_drawdown": float(drawdown.min()),
        "avg_turnover": float(turnover.mean()),
        "hit_rate": float((pnl > 0).mean()),
        "skew": float(pnl.skew()),
        "kurtosis": float(pnl.kurtosis()),
        "avg_gross_exposure": float(w.abs().sum(axis=1).mean()),
    }


def deflated_sharpe(
    observed_sharpe: float,
    n_trials: int,
    n_periods: int,
    *,
    skew: float = 0.0,
    kurtosis: float = 3.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    """Deflated Sharpe Ratio probability (Bailey & Lopez de Prado 2014).

    Returns P(true Sharpe > 0) after correcting the observed (annualized)
    Sharpe for multiple testing (``n_trials`` — supplied by the hypothesis
    ledger, never guessed), track length, skew, and excess kurtosis.

    ``kurtosis`` is the *raw* fourth moment ratio (normal = 3), matching
    pandas' ``kurtosis() + 3``.
    """
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    if n_periods < 2:
        raise ValueError("n_periods must be >= 2")

    # Work in per-period units.
    sr = observed_sharpe / math.sqrt(periods_per_year)

    # Expected maximum Sharpe among n_trials zero-true-Sharpe trials
    # (Euler-Mascheroni approximation of E[max of n std normals]).
    if n_trials == 1:
        sr_benchmark = 0.0
    else:
        gamma = 0.5772156649015329
        e = math.e
        from statistics import NormalDist

        nd = NormalDist()
        z1 = nd.inv_cdf(1.0 - 1.0 / n_trials)
        z2 = nd.inv_cdf(1.0 - 1.0 / (n_trials * e))
        # Cross-sectional std of trial Sharpes is unknowable without the ledger's
        # score history; the standard conservative choice is the observed sr's
        # own estimation-error scale.
        sr_std = math.sqrt(1.0 / n_periods)
        sr_benchmark = sr_std * ((1.0 - gamma) * z1 + gamma * z2)

    denom = math.sqrt(
        max(1e-12, 1.0 - skew * sr + ((kurtosis - 1.0) / 4.0) * sr**2)
    )
    z = ((sr - sr_benchmark) * math.sqrt(n_periods - 1)) / denom

    from statistics import NormalDist

    return NormalDist().cdf(z)
