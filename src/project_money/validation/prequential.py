"""Prequential (one-step-ahead, past-only) codelength evaluation.

The MDL tutorial's "honest" universal-code statistic (synthesis §3.6): a
forecaster is scored by its accumulated one-step-ahead log loss with parameters
refit only on the past — train and test never overlap by construction, and the
total is a codelength in nats. A candidate model has discovered structure only
if its prequential codelength beats the null forecaster's on the same data.
"""

from __future__ import annotations

import math
from typing import Callable, Protocol

import numpy as np
import pandas as pd


class Forecaster(Protocol):
    """A forecaster maps a past-only history to a predictive (mean, std) for
    the next observation."""

    def __call__(self, past: pd.Series) -> tuple[float, float]: ...


def gaussian_null_forecaster(past: pd.Series) -> tuple[float, float]:
    """The null: zero predictable mean, expanding-window volatility.

    A strategy/model that cannot out-compress this has found nothing beyond
    scale (see docs/agent_tooling_synthesis.md §3.6).
    """
    std = float(past.std(ddof=1))
    if not np.isfinite(std) or std <= 0.0:
        std = 1e-8
    return 0.0, std


def prequential_log_loss(
    series: pd.Series,
    forecaster: Callable[[pd.Series], tuple[float, float]],
    *,
    min_history: int = 30,
) -> float:
    """Accumulated one-step-ahead Gaussian log loss (nats) of ``forecaster``
    over ``series``, refit on strictly-past data at every step.

    Lower is better; differences between two forecasters on the same series are
    codelength differences (nats of evidence). Deterministic given inputs.
    """
    values = series.dropna()
    n = len(values)
    if n <= min_history:
        raise ValueError(f"need more than min_history={min_history} observations, got {n}")

    total = 0.0
    for i in range(min_history, n):
        past = values.iloc[:i]
        x = float(values.iloc[i])
        mu, sigma = forecaster(past)
        sigma = max(float(sigma), 1e-8)
        total += 0.5 * math.log(2.0 * math.pi * sigma**2) + ((x - mu) ** 2) / (2.0 * sigma**2)
    return total


def codelength_edge_nats(
    series: pd.Series,
    candidate: Callable[[pd.Series], tuple[float, float]],
    *,
    min_history: int = 30,
) -> float:
    """Nats saved by ``candidate`` relative to the Gaussian null on ``series``.

    Positive = the candidate compresses the series better than the null —
    the discovery criterion. Negative or ~0 = nothing found.
    """
    null_cl = prequential_log_loss(series, gaussian_null_forecaster, min_history=min_history)
    cand_cl = prequential_log_loss(series, candidate, min_history=min_history)
    return null_cl - cand_cl
