"""Known-zero negative controls — data provably (constructively) devoid of the
phenomenon under test.

The coffee-automaton discipline (synthesis §3.7): a metric that "lights up" on
these controls is measuring an artifact, and no result computed with it is
admissible until the artifact is isolated and differentially fixed.

All generators take an explicit ``seed`` — determinism is a gate.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd


def permute_returns(returns: pd.Series, seed: int) -> pd.Series:
    """IID shuffle of a return series: destroys all temporal structure while
    preserving the marginal distribution exactly. Any timing/momentum metric
    should read ~zero on this control."""
    rng = np.random.default_rng(seed)
    values = returns.to_numpy(copy=True)
    rng.shuffle(values)
    return pd.Series(values, index=returns.index, name=returns.name)


def block_permute_returns(returns: pd.Series, seed: int, *, block: int = 5) -> pd.Series:
    """Circular block permutation: preserves short-range autocorrelation inside
    blocks of length ``block`` while destroying structure at longer horizons.
    The control for metrics that should only respond to long-horizon effects."""
    if block < 1:
        raise ValueError("block must be >= 1")
    rng = np.random.default_rng(seed)
    values = returns.to_numpy(copy=True)
    n = len(values)
    n_blocks = int(np.ceil(n / block))
    # circular blocks so every observation appears exactly once
    starts = rng.integers(0, n, size=n_blocks)
    out = np.concatenate([values[(s + np.arange(block)) % n] for s in starts])[:n]
    return pd.Series(out, index=returns.index, name=returns.name)


def matched_gaussian_surrogate(returns: pd.Series, seed: int) -> pd.Series:
    """IID Gaussian surrogate matched to the series' mean and variance:
    the analytically-null world where any structure metric has a known-zero
    expectation."""
    rng = np.random.default_rng(seed)
    out = rng.normal(loc=float(returns.mean()), scale=float(returns.std(ddof=1)), size=len(returns))
    return pd.Series(out, index=returns.index, name=returns.name)


def known_zero_battery(
    metric_fn: Callable[[pd.Series], float],
    returns: pd.Series,
    *,
    n_trials: int = 100,
    seed: int = 0,
    control: Callable[[pd.Series, int], pd.Series] = permute_returns,
) -> dict[str, float]:
    """Run ``metric_fn`` on ``n_trials`` known-zero controls of ``returns``.

    Returns the null distribution summary and the observed metric's percentile
    within it. Interpretation contract:
    - ``observed_percentile`` near 1.0 → the observed value stands out from the
      null (necessary, not sufficient, for a finding).
    - a *wide* null spread or nonzero ``null_mean`` → the metric itself has an
      artifact at this sample size; falsify before use.
    """
    if n_trials < 2:
        raise ValueError("n_trials must be >= 2")
    observed = float(metric_fn(returns))
    null_values = np.array(
        [float(metric_fn(control(returns, seed + i))) for i in range(n_trials)]
    )
    return {
        "observed": observed,
        "null_mean": float(null_values.mean()),
        "null_std": float(null_values.std(ddof=1)),
        "null_p95": float(np.quantile(null_values, 0.95)),
        "observed_percentile": float((null_values < observed).mean()),
        "n_trials": float(n_trials),
    }
