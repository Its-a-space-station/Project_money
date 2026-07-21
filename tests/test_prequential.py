import numpy as np
import pandas as pd
import pytest

from project_money.validation.prequential import (
    codelength_edge_nats,
    gaussian_null_forecaster,
    prequential_log_loss,
)


def ar1_forecaster(past: pd.Series) -> tuple[float, float]:
    """Past-only AR(1) forecaster: phi estimated on history, expanding vol."""
    x = past.to_numpy()
    if len(x) < 3:
        return 0.0, max(float(np.std(x, ddof=1)), 1e-8)
    x0, x1 = x[:-1], x[1:]
    denom = float(np.dot(x0, x0))
    phi = float(np.dot(x0, x1) / denom) if denom > 0 else 0.0
    resid = x1 - phi * x0
    sigma = max(float(np.std(resid, ddof=1)), 1e-8)
    return phi * float(x[-1]), sigma


class TestPrequential:
    def test_ar_structure_gives_positive_edge(self):
        """Fail-before/pass-after: on a genuinely AR(1) series the AR
        forecaster must out-compress the null..."""
        rng = np.random.default_rng(7)
        n = 500
        x = np.zeros(n)
        for t in range(1, n):
            x[t] = 0.5 * x[t - 1] + rng.normal(0, 1)
        series = pd.Series(x)
        edge = codelength_edge_nats(series, ar1_forecaster)
        assert edge > 5.0  # decisive evidence in nats

    def test_pure_noise_gives_no_edge(self):
        """...and on IID noise it must find ~nothing (small |edge|)."""
        rng = np.random.default_rng(11)
        series = pd.Series(rng.normal(0, 1, 500))
        edge = codelength_edge_nats(series, ar1_forecaster)
        assert edge < 5.0

    def test_deterministic(self):
        rng = np.random.default_rng(3)
        series = pd.Series(rng.normal(0, 1, 200))
        a = prequential_log_loss(series, gaussian_null_forecaster)
        b = prequential_log_loss(series, gaussian_null_forecaster)
        assert a == b

    def test_too_short_raises(self):
        with pytest.raises(ValueError):
            prequential_log_loss(pd.Series(np.arange(10.0)), gaussian_null_forecaster)
