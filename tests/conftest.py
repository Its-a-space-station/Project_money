"""Shared deterministic fixtures. Every random draw has a fixed seed —
non-determinism in this suite is a bug (DS2 doctrine)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

N_DAYS = 400
N_ASSETS = 4


@pytest.fixture()
def dates() -> pd.DatetimeIndex:
    return pd.bdate_range("2020-01-01", periods=N_DAYS)


@pytest.fixture()
def prices(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Clean synthetic price panel: geometric random walks with mild drift,
    one asset given genuine positive autocorrelation (momentum structure)."""
    rng = np.random.default_rng(42)
    rets = rng.normal(0.0003, 0.01, size=(N_DAYS, N_ASSETS))
    # asset 0: AR(1) structure so momentum signals have something real to find
    for t in range(1, N_DAYS):
        rets[t, 0] += 0.35 * rets[t - 1, 0]
    prices = 100.0 * np.exp(np.cumsum(rets, axis=0))
    return pd.DataFrame(prices, index=dates, columns=[f"A{i}" for i in range(N_ASSETS)])


@pytest.fixture()
def returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def causal_momentum_signal(prices: pd.DataFrame) -> pd.DataFrame:
    """A properly causal signal: sign of trailing 20-day return, equal weight,
    long-only, normalized to gross <= 1. Uses only past data at every date."""
    mom = prices.pct_change(20)
    raw = (mom > 0).astype(float)
    gross = raw.sum(axis=1).replace(0, np.nan)
    return raw.div(gross, axis=0).fillna(0.0)


def lookahead_signal(prices: pd.DataFrame) -> pd.DataFrame:
    """A deliberately contaminated signal: weights proportional to each
    asset's FULL-SAMPLE mean return (future information at every date)."""
    full_mean = prices.pct_change().mean()  # uses the whole sample — leak
    w = (full_mean > full_mean.median()).astype(float)
    weights = pd.DataFrame(
        np.tile(w.to_numpy(), (len(prices), 1)),
        index=prices.index,
        columns=prices.columns,
    )
    gross = weights.sum(axis=1).replace(0, np.nan)
    return weights.div(gross, axis=0).fillna(0.0)
