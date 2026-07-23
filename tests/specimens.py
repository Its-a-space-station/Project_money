"""Synthetic reconstructions of the batch-6 known-bad specimens.

Each generator reproduces the *leak mechanism* of a documented paper the
verification harness must reject (stock_market_synthesis.md §9), using small
deterministic synthetic data — never the paper's data. Calibration-first
doctrine: prove the falsification battery on known junk before trusting any
pass; a specimen the harness fails to reject is a hole in the harness.

Fixed seeds throughout — non-determinism in these fixtures is a bug (DS2).

Specimen coverage grows as detectors land:
  - S6  intra-bar OHLC leakage ............... Mehtab & Sen "Case III" (94.76%)
  (later: S10 Nabipour flat-horizon, S9 CNN-LSTM shuffle, S5/S8 FNSPID, ...)
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from project_money.leakage import VintageRecord


def synthetic_ohlc_bars(n_bars: int = 300, *, seed: int = 7, start: str = "2020-01-01") -> pd.DataFrame:
    """A clean, internally consistent synthetic OHLCV panel: geometric-random-walk
    closes, opens that gap modestly from the prior close, and high/low that
    bracket the open/close. Used as the base grid for intra-bar specimens."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, periods=n_bars)
    rets = rng.normal(0.0003, 0.01, size=n_bars)
    close = 100.0 * np.exp(np.cumsum(rets))
    prev_close = np.concatenate([[close[0]], close[:-1]])
    open_ = prev_close * (1.0 + rng.normal(0.0, 0.003, size=n_bars))
    high = np.maximum(open_, close) * (1.0 + np.abs(rng.normal(0.0, 0.004, size=n_bars)))
    low = np.minimum(open_, close) * (1.0 - np.abs(rng.normal(0.0, 0.004, size=n_bars)))
    volume = rng.integers(1_000, 10_000, size=n_bars).astype(float)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=dates,
    )


# --- S6: intra-bar contemporaneous leakage (Mehtab & Sen "Case III") ----------

def mehtab_sen_intrabar_leak_signal(bars: pd.DataFrame) -> pd.Series:
    """The Case-III leak: 'predict' the open-return direction of bar t using bar
    t's own close — a value not known until the bar ends. Trivially near-perfect
    (the reported 94.76% OOS accuracy). Decision is nominally at the open."""
    return np.sign(bars["close"] - bars["open"]).rename("position")


def causal_gap_signal(bars: pd.DataFrame) -> pd.Series:
    """A properly causal counterpart deciding at the open of bar t: it uses only
    the open of t and the close of t-1, both known at decision time. Invariant to
    bar t's high/low/close, so the S6 detector must pass it."""
    prev_close = bars["close"].shift(1)
    return np.sign(bars["open"] - prev_close).fillna(0.0).rename("position")


# --- S6 evasions surfaced by the research-skeptic red-team (regression) --------
# Each is a genuinely leaky (or genuinely causal) signal that broke the first
# draft of the detector; the hardened detector must handle each correctly.

def _naive_grid_positions(n_bars: int, *, min_history: int = 30, n_test_bars: int = 8) -> np.ndarray:
    """The evenly-spaced grid the first (broken) detector exposed — recomputable
    by a signal, hence gameable. Used only to build the grid-gaming specimen."""
    usable = np.arange(min_history, n_bars)
    return np.unique(
        np.linspace(usable[0], usable[-1], num=min(n_test_bars, len(usable)), dtype=int)
    )


def grid_gaming_intrabar_leak_signal(bars: pd.DataFrame) -> pd.Series:
    """FN-1: reproduces the Case-III leak on every bar EXCEPT the bars a naive
    evenly-spaced grid would test — an optimizer that recomputes the verifier's
    grid. The exhaustive detector must still catch it (the leak lives elsewhere)."""
    leak = np.sign(bars["close"].to_numpy() - bars["open"].to_numpy())
    leak[_naive_grid_positions(len(bars))] = 0.0
    return pd.Series(leak, index=bars.index, name="position")


def subatol_intrabar_leak_signal(bars: pd.DataFrame) -> pd.Series:
    """FN-3: the Case-III leak scaled below the absolute tolerance. A downstream
    sign()/rank recovers it in full, so the sign-change check must catch it."""
    return pd.Series(
        1e-12 * np.sign(bars["close"].to_numpy() - bars["open"].to_numpy()),
        index=bars.index,
        name="position",
    )


def threshold_band_intrabar_leak_signal(bars: pd.DataFrame) -> pd.Series:
    """FN-2: the Case-III leak keyed to a 3% intraday move — inside the old
    (2%,5%) probe blind band. The wide, vol-scaled perturbation set must provoke
    it."""
    r = bars["close"].to_numpy() / bars["open"].to_numpy() - 1.0
    return pd.Series(
        np.where(r > 0.03, 1.0, np.where(r < -0.03, -1.0, 0.0)),
        index=bars.index,
        name="position",
    )


def nondeterministic_causal_signal(bars: pd.DataFrame) -> pd.Series:
    """FP-1: causal (uses only open_t and close_{t-1}) but nondeterministic —
    fresh RNG each call. Must be reported as nondeterministic, NOT as leakage."""
    base = np.sign(bars["open"] - bars["close"].shift(1)).fillna(0.0).to_numpy()
    return pd.Series(base + np.random.normal(0, 1e-6, len(bars)), index=bars.index, name="position")


def noncausal_string_signal(bars: pd.DataFrame) -> pd.Series:
    """R-1: non-numeric labels — must fail closed, never crash the gate."""
    vals = np.where(bars["close"].to_numpy() - bars["open"].to_numpy() > 0, "long", "flat")
    return pd.Series(vals, index=bars.index, name="position")


class MemoizingIntrabarLeak:
    """Round-2 HIGH: a date-keyed memoizer. It computes the Case-III leak the
    first time it sees each date (on the real bars) and returns the cached value
    thereafter — so same-index perturbation calls get stale (unchanged) output
    and the direct test is blind. The cold-reindex statefulness probe must flag
    it (a fresh date forces recomputation on the perturbed values)."""

    def __init__(self) -> None:
        self.cache: dict = {}

    def __call__(self, bars: pd.DataFrame) -> pd.Series:
        out = np.empty(len(bars))
        close = bars["close"].to_numpy()
        open_ = bars["open"].to_numpy()
        for i, dt in enumerate(bars.index):
            if dt not in self.cache:
                self.cache[dt] = float(np.sign(close[i] - open_[i]))
            out[i] = self.cache[dt]
        return pd.Series(out, index=bars.index, name="position")


def dc_offset_squash_leak_signal(bars: pd.DataFrame) -> pd.Series:
    """Round-2 MEDIUM: pin the sign with a large DC offset and carry the Case-III
    leak in a sub-tolerance magnitude. A downstream demean+sign recovers it. The
    tight absolute tolerance (no rtol·|value| inflation) must catch the move."""
    leak = 1e-6 * (bars["close"].to_numpy() - bars["open"].to_numpy())
    return pd.Series(1e6 + leak, index=bars.index, name="position")


def turn_of_month_seasonality_signal(bars: pd.DataFrame) -> pd.Series:
    """Round-3 Finding 1 (must PASS): a legitimate, causal calendar/seasonality
    signal — long in the last 3 calendar days of the month. The calendar is known
    in advance, so using it at the open is fully causal and pure; the statefulness
    probe must NOT false-flag it (the cold-no-perturb baseline classifies it as
    calendar-dependent, not memoization)."""
    idx = bars.index
    days_left = idx.days_in_month - idx.day
    return pd.Series(np.where(days_left <= 3, 1.0, 0.0), index=idx, name="position")


def volume_intrabar_leak_signal(bars: pd.DataFrame) -> pd.Series:
    """Round-3 Finding 4 (must be CAUGHT): a volume-only intra-bar leak — decides
    at the open using bar t's settled volume (known only at the close). The
    absolute volume probes (incl. a zero) must provoke it."""
    med = bars["volume"].median()
    return pd.Series(
        np.where(bars["volume"].to_numpy() > med, 1.0, 0.0), index=bars.index, name="position"
    )


class ComputeOnceIntrabarLeak:
    """Round-3 Finding 2 (KNOWN LIMITATION — needs isolation): caches the Case-III
    leak on the FIRST call and returns it verbatim forever, ignoring index AND
    values. Because ``base`` is itself the cached leak, no compare-to-base probe
    can catch it; only process/object isolation can. Documented via an xfail."""

    def __init__(self) -> None:
        self._v = None

    def __call__(self, bars: pd.DataFrame) -> pd.Series:
        if self._v is None:
            self._v = np.sign(bars["close"].to_numpy() - bars["open"].to_numpy())
        return pd.Series(self._v, index=bars.index, name="position")


# --- S9: shuffle-then-split leakage (CNN-LSTM shuffled series) -----------------

def cnn_lstm_shuffled_split(
    n_obs: int = 400, *, seed: int = 11, train_frac: float = 0.8, start: str = "2020-01-01"
) -> tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    """The specimen: permute the row order of a serially-correlated series, THEN
    split. Train and test timestamps interleave in time, so the test set sits at
    and before the last train timestamp — the leak the S9 detector must reject."""
    idx = pd.bdate_range(start, periods=n_obs)
    order = np.random.default_rng(seed).permutation(n_obs)
    cut = int(n_obs * train_frac)
    return idx[np.sort(order[:cut])], idx[np.sort(order[cut:])]


def causal_forward_split(
    n_obs: int = 400, *, train_frac: float = 0.8, start: str = "2020-01-01"
) -> tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    """A proper forward holdout: train is the earlier contiguous block, test the
    strictly-later one. The S9 detector must pass it."""
    idx = pd.bdate_range(start, periods=n_obs)
    cut = int(n_obs * train_frac)
    return idx[:cut], idx[cut:]


# --- S5 / S10: level-forecast + flat-horizon leakage (Nabipour) ---------------

def nabipour_level_forecast(
    n_obs: int = 400, *, seed: int = 13, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """The specimen: a 'forecast' of price LEVELS that tracks the actual almost
    perfectly (R²≈1.0) — the near-integrated levels make even this trivial. Must
    trip S5 (level R² + level-lag)."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n_obs)))
    y_true = pd.Series(close, index=idx, name="level")
    y_pred = y_true * (1.0 + rng.normal(0.0, 1e-4, n_obs))  # near-perfect level tracking
    return y_true, y_pred.rename("pred")


def nabipour_horizon_errors() -> dict[int, float]:
    """Flat OOS error across 1→30-day horizons (the Nabipour fingerprint): a
    genuinely predictive model degrades with horizon, so a flat curve trips S10."""
    return {1: 0.0100, 5: 0.0100, 10: 0.0101, 20: 0.0101, 30: 0.0102}


def honest_returns_forecast(
    n_obs: int = 400, *, seed: int = 17, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """A causal counterpart: forecasting RETURNS (not levels) with a weak, honest
    signal — low R², no level-lag. S5 must pass it."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    y_true = pd.Series(rng.normal(0.0, 0.01, n_obs), index=idx, name="ret")
    y_pred = pd.Series(0.05 * y_true.to_numpy() + rng.normal(0.0, 0.01, n_obs), index=idx, name="pred")
    return y_true, y_pred


def growing_horizon_errors() -> dict[int, float]:
    """A causal counterpart: OOS error that grows with horizon. S10 must pass it."""
    return {1: 0.5, 5: 0.9, 10: 1.4, 20: 2.1, 30: 3.0}


def level_forecast_threshold_dodge(
    n_obs: int = 400, *, seed: int = 23, noise_frac: float = 0.25, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """S5 red-team #1 (must be CAUGHT): a near-perfect LEVEL forecast degraded with
    noise ~ noise_frac of the level dispersion so R² drops just past 0.95 — the old
    fixed-R² bar missed it. Reported honestly (is_levels=True), it must still fail:
    it does not beat the persistence null (skill << 0)."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n_obs)))
    y_true = pd.Series(close, index=idx, name="level")
    y_pred = y_true + noise_frac * float(y_true.std()) * rng.normal(0.0, 1.0, n_obs)
    return y_true, y_pred.rename("pred")


def contemporaneous_returns_leak(
    n_obs: int = 400, *, seed: int = 29, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """S5 red-team #2 (must be CAUGHT): a returns 'forecast' that is essentially the
    contemporaneous target (R²≈1), declared is_levels=False to dodge the level
    checks. The unconditional too-high-R² flag must catch it regardless."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    y_true = pd.Series(rng.normal(0.0, 0.01, n_obs), index=idx, name="ret")
    y_pred = (y_true + rng.normal(0.0, 1e-5, n_obs)).rename("pred")
    return y_true, y_pred


def ar_momentum_returns_forecast(
    n_obs: int = 400, *, seed: int = 31, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """S5 red-team #5 (must PASS): a legitimate causal AR/momentum returns forecast
    ŷ_t = k·r_{t-1}. It correlates perfectly with the lagged *return*, but on
    RETURNS that is genuine signal, not repackaged persistence — the level-lag
    check must not false-flag it (returns are not inferred as levels)."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    r = np.zeros(n_obs)
    for t in range(1, n_obs):
        r[t] = 0.2 * r[t - 1] + rng.normal(0.0, 0.01)
    y_true = pd.Series(r, index=idx, name="ret")
    y_pred = pd.Series(np.concatenate([[0.0], 0.2 * r[:-1]]), index=idx, name="pred")
    return y_true, y_pred


def returns_contemporaneous_leak_moderate(
    n_obs: int = 400, *, seed: int = 37, k: float = 0.3, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """S5 round-2 #1 (must be CAUGHT): a daily-returns contemporaneous leak tuned to
    a moderate R² (~0.9), below the old 0.99 bar. Low-autocorrelation returns → the
    returns R² bar (0.15) must catch it."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    y_true = pd.Series(rng.normal(0.0, 0.01, n_obs), index=idx, name="ret")
    y_pred = (y_true + k * 0.01 * rng.normal(0.0, 1.0, n_obs)).rename("pred")
    return y_true, y_pred


def overlapping_returns_honest_forecast(
    n_obs: int = 400, *, window: int = 20, seed: int = 41, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """S5 round-2 #2 (must PASS): an honest weak forecast of overlapping k-day
    returns — autocorrelated but stationary, so lag-1 autocorrelation would
    misclassify it as levels. Integratedness inference routes it to the abstain
    regime; no false positive."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    daily = pd.Series(rng.normal(0.0003, 0.01, n_obs), index=idx)
    overlap = daily.rolling(window).sum().dropna()
    y_pred = (0.1 * overlap.shift(1)).fillna(0.0).rename("pred")
    return overlap.rename("ret"), y_pred


def strong_but_honest_returns_forecast(
    n_obs: int = 400, *, seed: int = 47, target_r2: float = 0.4, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """S5 round-3 #3 (must PASS): a rare but genuine strong returns edge (R²≈0.4).
    Most honest returns edges are R²<0.05, but a low-noise / cross-sectional signal
    can be stronger — S5 must not HARD-reject the rare winner (returns bar raised to
    0.5, framed as review). Low-autocorrelation returns regime."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    signal = rng.normal(0.0, 0.01, n_obs)
    noise_sd = 0.01 * ((1.0 - target_r2) / target_r2) ** 0.5
    y_true = pd.Series(signal + rng.normal(0.0, noise_sd, n_obs), index=idx, name="ret")
    y_pred = pd.Series(signal, index=idx, name="pred")  # forecasts the true signal component
    return y_true, y_pred


def trending_level_plausible_leak(
    n_obs: int = 400, *, seed: int = 43, k: float = 0.11, start: str = "2020-01-01"
) -> tuple[pd.Series, pd.Series]:
    """S5 round-2 #3 (must be CAUGHT): a contemporaneous leak on a random-walk level
    that threads under the old 0.99 R² bar. A random walk is near-unforecastable, so
    the integrated regime (skill bounds + R² backstop) must flag it."""
    idx = pd.bdate_range(start, periods=n_obs)
    rng = np.random.default_rng(seed)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n_obs)))
    y_true = pd.Series(close, index=idx, name="level")
    y_pred = (y_true + k * float(y_true.std()) * rng.normal(0.0, 1.0, n_obs)).rename("pred")
    return y_true, y_pred


# --- S9-scaler / S11 / S16: Paper 8 compound leak -----------------------------

def paper8_scaler_leak_signal(prices: pd.DataFrame) -> pd.DataFrame:
    """Paper 8 scaler-leak: min-max scale the WHOLE price panel (fit on train+test)
    before forming the signal — a non-causal transform. check_no_lookahead must
    catch it (truncation changes the full-sample min/max)."""
    scaled = (prices - prices.min()) / (prices.max() - prices.min())  # full-sample min/max — leak
    w = (scaled > 0.5).astype(float)
    gross = w.sum(axis=1).replace(0, np.nan)
    return w.div(gross, axis=0).fillna(0.0)


def paper8_impossible_accuracy() -> float:
    """Paper 8's reported OOS directional accuracy (in its 0.96–0.99 band). S11
    must flag it as implausible."""
    return 0.973


def paper8_cost_free_result() -> dict[str, float]:
    """Paper 8's cost-free backtest metrics. S16 must flag the zero cost."""
    return {"cost_bps": 0.0, "sharpe_gross": 2.4, "sharpe_net": 2.4}


# --- S7 / S8: non-causal transform leakage (decomposition / feature construction) ---
# Each non-causal transform is a preprocessing step fit on the WHOLE sample — the
# leak class purge/embargo walk-forward misses; check_causal_transform must catch
# it, and pass the causal (past-only) counterpart.

def global_minmax_transform(data: pd.DataFrame) -> pd.DataFrame:
    """S8: min-max scaling fit on the whole sample (per column) — non-causal."""
    rng = (data.max() - data.min()).replace(0, np.nan)
    return (data - data.min()) / rng


def expanding_minmax_transform(data: pd.DataFrame) -> pd.DataFrame:
    """Causal counterpart: expanding (past-only) min-max scaling."""
    lo = data.expanding().min()
    hi = data.expanding().max()
    return (data - lo) / (hi - lo).replace(0, np.nan)


def full_sample_detrend_transform(data: pd.DataFrame) -> pd.DataFrame:
    """S7: subtract a linear trend fit on the whole sample (a decomposition fit on
    the test data), per column — non-causal."""
    t = np.arange(len(data), dtype=float)
    out = {col: data[col].to_numpy(dtype=float) - np.polyval(
        np.polyfit(t, data[col].to_numpy(dtype=float), 1), t
    ) for col in data.columns}
    return pd.DataFrame(out, index=data.index)


def expanding_detrend_transform(data: pd.DataFrame) -> pd.DataFrame:
    """Causal counterpart: subtract the expanding (past-only) mean."""
    return data - data.expanding().mean()


def centered_smooth_transform(data: pd.DataFrame) -> pd.DataFrame:
    """S8: centered rolling mean — bidirectional, uses future points (non-causal)."""
    return data.rolling(5, center=True, min_periods=1).mean()


def trailing_smooth_transform(data: pd.DataFrame) -> pd.DataFrame:
    """Causal counterpart: trailing rolling mean."""
    return data.rolling(5, min_periods=1).mean()


# --- shared causality-core red-team regressions (harden check_no_lookahead too) ---

# The evenly-spaced cutoff grid the OLD core used (n=400, min_history=30) — the
# positions a leak could dodge onto. The hardened core tests every row instead.
_NAIVE_LOOKAHEAD_GRID = [30, 82, 135, 188, 240, 293, 346, 399]


def grid_gamed_lookahead_signal(prices: pd.DataFrame) -> pd.DataFrame:
    """Core Finding 1 (CRITICAL): a 1-day lookahead (weights from NEXT day's move)
    zeroed on exactly the old 8-cutoff grid rows. A finite-horizon leak shows only
    at the boundary row, so evenly-spaced cutoffs missed it — exhaustive cutoffs
    must catch it on the ungamed rows."""
    fut_up = (prices.shift(-1) > prices).astype(float)  # uses next day — lookahead
    gross = fut_up.sum(axis=1).replace(0, np.nan)
    w = fut_up.div(gross, axis=0).fillna(0.0)
    for p in _NAIVE_LOOKAHEAD_GRID:
        if p < len(w):
            w.iloc[p] = 0.0
    return w


def tail_fullsample_leak_transform(data: pd.DataFrame) -> pd.DataFrame:
    """Core Finding 2 (HIGH): identity except the most-recent 10% of rows are
    divided by the FULL-sample max — a leak in the tail the old grid never tested
    (the newest data a deployed signal acts on). Exhaustive cutoffs must catch it."""
    out = data.copy()
    tail = int(len(data) * 0.9)
    out.iloc[tail:] = data.iloc[tail:] / data.max()
    return out


class StatefulCountingTransform:
    """Core Finding 6: cross-call state makes the output vary between calls — must be
    reported as stateful/nondeterministic, NOT mislabeled 'non-causal transform'."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, data: pd.DataFrame) -> pd.DataFrame:
        self.calls += 1
        return data.rolling(5, min_periods=1).mean() * self.calls


def string_output_transform(data: pd.DataFrame) -> pd.DataFrame:
    """Core Finding 7: non-numeric output must fail closed, not crash."""
    return pd.DataFrame("x", index=data.index, columns=data.columns)


def column_dropping_transform(data: pd.DataFrame) -> pd.DataFrame:
    """Core Finding 8: a shape change under truncation must fail closed, not crash."""
    out = data.copy()
    if len(data) < 400:
        out = out.drop(columns=[data.columns[0]])
    return out


class FitOnceScaler:
    """Core Finding 3 (KNOWN LIMITATION — needs isolation): fits mean/std on its
    first call (the full panel) and freezes them, so every truncated recompute
    reuses the full-sample params and matches. A full-sample-fit scaler that evades
    in-process execute-and-compare; the transform analogue of ComputeOnce."""

    def __init__(self) -> None:
        self.mu = None
        self.sigma = None

    def __call__(self, data: pd.DataFrame) -> pd.DataFrame:
        if self.mu is None:
            self.mu = data.mean()
            self.sigma = data.std().replace(0, np.nan)
        return (data - self.mu) / self.sigma


# --- S26: calibration axis (ECE) ----------------------------------------------

def well_calibrated_forecast(n_obs: int = 5000, *, seed: int = 101) -> tuple[np.ndarray, np.ndarray]:
    """S26 (must PASS): predicted probabilities whose realized frequencies match —
    outcomes drawn as Bernoulli(p). Low ECE by construction."""
    rng = np.random.default_rng(seed)
    p = rng.uniform(0.05, 0.95, n_obs)
    y = (rng.random(n_obs) < p).astype(float)
    return p, y


def overconfident_forecast(n_obs: int = 5000, *, seed: int = 103) -> tuple[np.ndarray, np.ndarray]:
    """S26 (must be FLAGGED): confident ~0.95 predictions but coin-flip outcomes —
    a large calibration gap (ECE ~ 0.45)."""
    rng = np.random.default_rng(seed)
    p = np.full(n_obs, 0.95)
    y = (rng.random(n_obs) < 0.5).astype(float)
    return p, y


def confident_tail_miscalibration(
    n_obs: int = 5000, *, tail_frac: float = 0.09, seed: int = 107
) -> tuple[np.ndarray, np.ndarray]:
    """S26 red-team Finding 2 (must be FLAGGED): a bulk of calibrated 0.5 calls plus
    a sparse tail predicted 0.99 whose outcome is always 0 — max-confidence, 100%
    wrong, exactly what a confidence-sized strategy levers up. Count-weighted ECE
    forgives it; MCE-with-count-floor must catch it."""
    rng = np.random.default_rng(seed)
    n_tail = int(n_obs * tail_frac)
    n_bulk = n_obs - n_tail
    p = np.concatenate([np.full(n_bulk, 0.5), np.full(n_tail, 0.99)])
    y = np.concatenate([(rng.random(n_bulk) < 0.5).astype(float), np.zeros(n_tail)])
    return p, y


def within_bin_anticalibration(n_obs: int = 5000, *, seed: int = 109) -> tuple[np.ndarray, np.ndarray]:
    """S26 red-team Finding 3 (must be FLAGGED): all mass in one wide uniform bin
    (0.4,0.5] at two sub-values whose reality is anti-correlated with confidence —
    mean_pred≈mean_outcome hides it at 10 bins; the finer-binning pass surfaces it."""
    rng = np.random.default_rng(seed)
    half = n_obs // 2
    p = np.concatenate([np.full(half, 0.401), np.full(n_obs - half, 0.499)])
    y = np.concatenate(
        [(rng.random(half) < 0.90).astype(float), np.zeros(n_obs - half)]
    )
    return p, y


def subfloor_confident_error(
    n_obs: int = 2000, *, cluster: int = 19, seed: int = 113
) -> tuple[np.ndarray, np.ndarray]:
    """S26 round-2 R2-1 (must be FLAGGED): a confident-wrong cluster BELOW the old
    MCE count floor (19 samples at 0.99 → outcome 0) inside a calibrated book. The
    per-bin studentized test (no count floor) must catch it regardless of count."""
    rng = np.random.default_rng(seed)
    n_bulk = n_obs - cluster
    p = np.concatenate([np.full(n_bulk, 0.5), np.full(cluster, 0.99)])
    y = np.concatenate([(rng.random(n_bulk) < 0.5).astype(float), np.zeros(cluster)])
    return p, y


def high_abstention_forecast(
    n_obs: int = 5000, *, answered: int = 500, seed: int = 111
) -> tuple[np.ndarray, np.ndarray]:
    """S26 red-team Finding 4 (must be FLAGGED): NaN (abstain) on most cases,
    calibrated on the few answered — the coverage floor must catch it."""
    rng = np.random.default_rng(seed)
    p = np.full(n_obs, np.nan)
    ans_idx = rng.choice(n_obs, answered, replace=False)
    pa = rng.uniform(0.05, 0.95, answered)
    p[ans_idx] = pa
    y = np.zeros(n_obs)
    y[ans_idx] = (rng.random(answered) < pa).astype(float)
    return p, y


# --- S3: model-vintage contamination (MarketSenseAI time-travel) ---------------

def marketsenseai_vintage_records() -> list[VintageRecord]:
    """The specimen: an LLM stock-picker whose training knowledge cutoff (2024)
    postdates the 'out-of-sample' window start (2024-01-01 below is inside its
    training) — 'time-travel' contamination. The existing vintage auditor must
    label it contaminated (S3)."""
    return [
        VintageRecord(
            "marketsenseai-llm",
            vintage_date=date(2023, 1, 1),
            knowledge_cutoff=date(2024, 6, 1),
        )
    ]
