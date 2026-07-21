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
        # pandas kurtosis() is EXCESS (Fisher; Gaussian = 0). deflated_sharpe
        # takes RAW kurtosis (Gaussian = 3) — feed it kurtosis_raw.
        "kurtosis": float(pnl.kurtosis()),
        "kurtosis_raw": float(pnl.kurtosis()) + 3.0,
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
    trial_sharpes: "list[float] | tuple[float, ...] | None" = None,
) -> float:
    """Deflated Sharpe Ratio probability (Bailey & Lopez de Prado 2014).

    Returns P(true Sharpe > 0) after correcting the observed (annualized)
    Sharpe for multiple testing (``n_trials`` — supplied by the hypothesis
    ledger, never guessed), track length, skew, and kurtosis.

    ``kurtosis`` is the *raw* fourth-moment ratio (Gaussian = 3) — i.e.
    pandas' ``kurtosis() + 3``, or ``compute_metrics``'s ``kurtosis_raw``.
    Values below 1 are mathematically impossible for raw kurtosis and raise,
    catching the excess-kurtosis convention mistake.

    ``trial_sharpes`` — the ANNUALIZED Sharpe estimates of the recorded
    trials (e.g. ``HypothesisLedger.recorded_sharpes()``). Per the source,
    the expected-max benchmark scales with **sqrt(V[{SR_n}]), the empirical
    variance of Sharpe estimates across trials**. When omitted, the IID
    zero-edge null approximation ``sqrt(1/n_periods)`` is used — documented
    fallback that UNDERSTATES the bar when trials are diverse (verified
    against the book, batch-3 review; see docs/ml_shelf_integration.md §1).
    """
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    if n_periods < 2:
        raise ValueError("n_periods must be >= 2")
    if kurtosis < 1.0:
        raise ValueError(
            f"kurtosis={kurtosis} is impossible for RAW kurtosis (Gaussian=3); "
            "you likely passed excess (Fisher) kurtosis — add 3, or use "
            "compute_metrics()['kurtosis_raw']"
        )

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
        if trial_sharpes is not None and len(trial_sharpes) >= 2:
            per_period = [s / math.sqrt(periods_per_year) for s in trial_sharpes]
            mean_pp = sum(per_period) / len(per_period)
            var_pp = sum((s - mean_pp) ** 2 for s in per_period) / (len(per_period) - 1)
            sr_std = math.sqrt(max(var_pp, 1e-18))
        else:
            # IID zero-edge null approximation: each trial's SR estimate on
            # n_periods observations has sampling std ~ sqrt(1/n_periods).
            # Understates the bar for genuinely diverse trials.
            sr_std = math.sqrt(1.0 / n_periods)
        sr_benchmark = sr_std * ((1.0 - gamma) * z1 + gamma * z2)

    denom = math.sqrt(
        max(1e-12, 1.0 - skew * sr + ((kurtosis - 1.0) / 4.0) * sr**2)
    )
    z = ((sr - sr_benchmark) * math.sqrt(n_periods - 1)) / denom

    from statistics import NormalDist

    return NormalDist().cdf(z)
