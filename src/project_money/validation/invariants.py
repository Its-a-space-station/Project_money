"""Stage-0 invariant checks — the cheap, deterministic screens every candidate
passes before any backtest spends compute.

Research-only. These functions *evaluate artifacts*; they never act.

The lookahead check implements the strongest known deterministic test: a
signal function is re-run on truncated histories and its output at the cutoff
must match the full-sample output. A function that uses any future information
(even subtly, e.g. full-sample normalization) fails this check. This is the
research analogue of Terminal-Bench's integrity-by-construction rule: do not
trust an agent's claim of causality — execute it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd


@dataclass
class CheckResult:
    """Outcome of one invariant check. ``passed`` is authoritative; ``reasons``
    lists every violation found (empty when passed)."""

    name: str
    passed: bool
    reasons: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:  # allow `if result:` idiom
        return self.passed


def check_data_integrity(
    prices: pd.DataFrame,
    *,
    max_nan_frac: float = 0.05,
    max_abs_return: float = 0.5,
) -> CheckResult:
    """Deterministic data-quality screen on a price panel (index = dates,
    columns = instruments).

    Violations collected (never silently dropped — verification-debt doctrine):
    non-monotonic or duplicated timestamps, non-positive prices, excessive NaN
    share per column, and single-bar returns beyond ``max_abs_return`` (likely
    bad adjustments; flagged for human review, not auto-scrubbed).
    """
    reasons: list[str] = []

    if not prices.index.is_monotonic_increasing:
        reasons.append("index not monotonically increasing")
    if prices.index.has_duplicates:
        reasons.append("index has duplicate timestamps")

    numeric = prices.select_dtypes(include=[np.number])
    if numeric.shape[1] != prices.shape[1]:
        non_numeric = sorted(set(prices.columns) - set(numeric.columns))
        reasons.append(f"non-numeric columns: {non_numeric}")

    if (numeric <= 0).any().any():
        bad = numeric.columns[(numeric <= 0).any()].tolist()
        reasons.append(f"non-positive prices in: {bad}")

    nan_frac = numeric.isna().mean()
    over = nan_frac[nan_frac > max_nan_frac]
    if not over.empty:
        reasons.append(
            f"NaN fraction exceeds {max_nan_frac:.2%} in: "
            + ", ".join(f"{c}={v:.2%}" for c, v in over.items())
        )

    rets = numeric.pct_change()
    extreme = rets.abs() > max_abs_return
    if extreme.any().any():
        n = int(extreme.sum().sum())
        cols = numeric.columns[extreme.any()].tolist()
        reasons.append(
            f"{n} single-bar returns beyond +/-{max_abs_return:.0%} in {cols} "
            "(possible bad adjustment; needs_human_review)"
        )

    return CheckResult("data_integrity", not reasons, reasons)


def check_weights_valid(
    weights: pd.DataFrame,
    *,
    max_gross: float = 1.0 + 1e-9,
    allow_short: bool = False,
) -> CheckResult:
    """Screen a weight panel (index = dates, columns = instruments) for
    structural validity: finite values, gross exposure within ``max_gross``,
    and (by default) no short weights.

    Note this is a *research artifact* check — weights describe a simulated
    allocation under study, never an instruction to act.
    """
    reasons: list[str] = []

    if not np.isfinite(weights.to_numpy(dtype=float, na_value=np.nan)).all():
        n_bad = int((~np.isfinite(weights.to_numpy(dtype=float, na_value=np.nan))).sum())
        reasons.append(f"{n_bad} non-finite weight entries (NaN/inf)")

    gross = weights.abs().sum(axis=1)
    if (gross > max_gross).any():
        worst = float(gross.max())
        reasons.append(f"gross exposure exceeds {max_gross:.4f} (max {worst:.4f})")

    if not allow_short and (weights < 0).any().any():
        reasons.append("negative weights present but allow_short=False")

    return CheckResult("weights_valid", not reasons, reasons)


def check_no_lookahead(
    signal_fn: Callable[[pd.DataFrame], pd.DataFrame],
    prices: pd.DataFrame,
    *,
    n_cutoffs: int = 8,
    min_history: int = 30,
    atol: float = 1e-10,
) -> CheckResult:
    """Execute-and-compare lookahead detector.

    ``signal_fn`` maps a price panel to a weight panel on the same index. For
    each of ``n_cutoffs`` evenly spaced cutoff dates t, the function is re-run
    on ``prices.loc[:t]`` and its **entire output** must equal the full-sample
    output over the overlapping window (within ``atol``): a causal function's
    value at any date s <= t depends only on data up to s, so truncation at t
    cannot change it. Comparing the whole window (not just the cutoff row)
    catches leaks that thresholding hides at the boundary — e.g. full-sample
    z-scoring, whose contamination shows up at *earlier* dates.

    Deterministic by construction: cutoffs are evenly spaced, not sampled.
    """
    reasons: list[str] = []

    full = signal_fn(prices)
    if not full.index.equals(prices.index):
        return CheckResult(
            "no_lookahead",
            False,
            ["signal_fn output index does not match input index"],
        )

    usable = prices.index[min_history:]
    if len(usable) == 0:
        return CheckResult("no_lookahead", False, ["not enough history for cutoff testing"])

    positions = np.linspace(0, len(usable) - 1, num=min(n_cutoffs, len(usable)), dtype=int)
    cutoffs = usable[positions]

    for t in cutoffs:
        truncated = signal_fn(prices.loc[:t])
        expected = full.loc[:t]
        if not truncated.index.equals(expected.index):
            reasons.append(f"cutoff {t}: truncated output index mismatch")
            continue
        tr = truncated.to_numpy(dtype=float)
        ex = expected.to_numpy(dtype=float)
        nan_tr, nan_ex = np.isnan(tr), np.isnan(ex)
        if (nan_tr != nan_ex).any():
            n_bad = int((nan_tr != nan_ex).sum())
            reasons.append(f"cutoff {t}: NaN pattern differs at {n_bad} entries — lookahead")
            continue
        valid = ~nan_tr
        if not np.allclose(tr[valid], ex[valid], atol=atol, rtol=0.0):
            diff = np.abs(tr[valid] - ex[valid])
            n_bad = int((diff > atol).sum())
            reasons.append(
                f"cutoff {t}: {n_bad} weight entries differ over the overlapping window "
                f"(max abs diff {float(diff.max()):.3e}) — lookahead"
            )

    return CheckResult("no_lookahead", not reasons, reasons)
