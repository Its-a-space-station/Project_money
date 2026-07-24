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

# --- failure dispositions (shared by CheckResult and the cascade) -------------
# A *failure*'s disposition, never an action word. ``reject`` hard-disqualifies a
# candidate; ``needs_human_review`` routes it to human adjudication instead of an
# auto-reject. Both are canonical research labels (docs/label_policy.md). The
# cascade turns a stage's disposition into the matching ``CascadeResult`` label
# (see cascade.run_cascade). ``reject`` is the safe default / fail-closed
# direction: an unknown disposition is always hardened to ``reject``, never
# softened to review.
REJECT = "reject"
NEEDS_HUMAN_REVIEW = "needs_human_review"
FAILURE_DISPOSITIONS = frozenset({REJECT, NEEDS_HUMAN_REVIEW})


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one invariant check. ``passed`` is authoritative; ``reasons``
    lists every violation found (empty when passed).

    Frozen: a validated disposition cannot be softened by post-hoc assignment
    (matching ``cascade.Stage``); build the ``reasons`` list before construction.

    ``disposition`` classifies a *failure* (ignored when ``passed``): ``reject``
    (default — a hard disqualification) or ``needs_human_review`` (a review flag a
    human must adjudicate, not an auto-reject). It lets a cascade emit the
    canonical ``needs_human_review`` label instead of hard-rejecting a legitimate
    strategy. A check that mixes fail-closed input errors (reject) with a
    substantive review flag reports the *most severe* disposition it tripped
    (reject outranks needs_human_review)."""

    name: str
    passed: bool
    reasons: list[str] = field(default_factory=list)
    disposition: str = REJECT

    def __post_init__(self) -> None:
        if self.disposition not in FAILURE_DISPOSITIONS:
            raise ValueError(
                f"disposition {self.disposition!r} not one of {sorted(FAILURE_DISPOSITIONS)}"
            )

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


def _coerce_output(out, expected_index: pd.Index, expected_ncols: int | None):
    """Coerce an ``fn`` output to a float matrix aligned to ``expected_index`` (and,
    if given, ``expected_ncols`` columns). Returns ``(matrix, None)`` or, on any
    structural fault, ``(None, reason)`` — so callers fail closed, never crash."""
    if isinstance(out, pd.Series):
        out = out.to_frame()
    if not isinstance(out, pd.DataFrame):
        return None, "output is not a Series/DataFrame — fail closed"
    if not out.index.equals(expected_index):
        return None, "output index does not match input index"
    try:
        mat = out.to_numpy(dtype=float)
    except (ValueError, TypeError):
        return None, "non-numeric output — fail closed"
    if expected_ncols is not None and mat.shape[1] != expected_ncols:
        return None, f"output column count changed ({mat.shape[1]} vs {expected_ncols}) — fail closed"
    return mat, None


def _rows_change(exp: np.ndarray, tr: np.ndarray, *, atol: float, rtol: float) -> str | None:
    """NaN-pattern + value change between two equal-shape matrices; reason or None."""
    nan_e, nan_t = np.isnan(exp), np.isnan(tr)
    if (nan_e != nan_t).any():
        return f"NaN pattern differs at {int((nan_e != nan_t).sum())} entries"
    valid = ~nan_e
    if valid.any() and not np.allclose(tr[valid], exp[valid], atol=atol, rtol=rtol):
        diff = np.abs(tr[valid] - exp[valid])
        n_bad = int((diff > atol + rtol * np.abs(exp[valid])).sum())
        return f"{n_bad} entries differ (max abs {float(diff.max()):.3e})"
    return None


def _whole_window_causal_check(
    fn: Callable[[pd.DataFrame], pd.DataFrame],
    data: pd.DataFrame,
    *,
    name: str,
    leak_label: str,
    min_history: int = 30,
    max_cutoffs: int | None = None,
    atol: float = 1e-10,
    rtol: float = 1e-9,
) -> CheckResult:
    """Shared whole-window execute-and-compare causality core.

    Re-runs ``fn`` on truncated inputs: a causal function's output at any row s is
    unchanged when the data after s is removed, so at cutoff t=s the boundary row
    reveals any leak that used data after s. Because a *finite-horizon* leak (e.g.
    a 1-day lookahead) is visible only at that boundary row, cutoffs are
    **exhaustive** — every row from ``min_history`` on becomes a boundary exactly
    once — rather than an evenly-spaced grid a leak could zero itself onto, and the
    most-recent rows (where a deployed signal acts) are covered. ``max_cutoffs``
    caps this to a dense stride for very large panels; that fast path is
    best-effort (a strided subset is in principle recomputable — verification
    debt), so exhaustive (the default) is the trustworthy mode.

    A determinism/statefulness pre-check runs ``fn`` twice on the full input; a
    result that differs is reported as stateful/nondeterministic (distinct from
    leakage), never mislabeled. Non-numeric / misaligned / shape-changing output
    fails closed. Comparison uses a relative tolerance so a legitimate causal
    transform with length-dependent float rounding on large-magnitude data is not
    false-rejected. NOTE a *compute-once / full-sample-fit* stateful ``fn`` (e.g. a
    scaler fit on its first, full-panel call) is NOT caught in-process — that needs
    process/instance isolation (verification debt; the ``ComputeOnce`` analogue).
    """
    full_mat, err = _coerce_output(fn(data), data.index, None)
    if err is not None:
        return CheckResult(name, False, [err])

    # Determinism / statefulness pre-check — a stale/varying fn cannot be audited.
    full_mat2, err2 = _coerce_output(fn(data), data.index, full_mat.shape[1])
    if err2 is not None or _rows_change(full_mat, full_mat2, atol=atol, rtol=rtol) is not None:
        return CheckResult(
            name,
            False,
            ["fn is nondeterministic or stateful across calls (two runs on identical input differ) "
             "— execute-and-compare cannot audit it; make it a pure, reset-per-call function (DS2)"],
        )

    n = len(data)
    if n <= min_history:
        return CheckResult(name, False, ["not enough history for cutoff testing"])

    positions = np.arange(min_history, n)  # exhaustive: no grid to game, tail covered
    if max_cutoffs is not None and len(positions) > max_cutoffs:
        stride = int(np.ceil(len(positions) / max_cutoffs))
        positions = positions[::stride]  # best-effort dense stride (recomputable → verification debt)

    reasons: list[str] = []
    ncols = full_mat.shape[1]
    for idx in positions:
        idx = int(idx)
        trunc_mat, err = _coerce_output(fn(data.iloc[: idx + 1]), data.index[: idx + 1], ncols)
        if err is not None:
            reasons.append(f"cutoff {data.index[idx]}: {err}")
            continue
        change = _rows_change(full_mat[: idx + 1], trunc_mat, atol=atol, rtol=rtol)
        if change is not None:
            reasons.append(f"cutoff {data.index[idx]}: {change} over the overlap — {leak_label}")

    return CheckResult(name, not reasons, reasons)


def check_causal_transform(
    transform_fn: Callable[[pd.DataFrame], pd.DataFrame],
    data: pd.DataFrame,
    *,
    min_history: int = 30,
    max_cutoffs: int | None = None,
    atol: float = 1e-10,
    rtol: float = 1e-9,
) -> CheckResult:
    """Whole-window causality check for a feature/preprocessing TRANSFORM — verifier
    items S7 (non-causal decomposition: EMD/EEMD/VMD/DWT/wavelet, correlation/
    covariance graphs) and S8 (non-causal feature construction: global min-max /
    standard scaling, bidirectional interpolation/spline, global smoothing).

    Generalizes ``check_no_lookahead`` from a weight panel to any numeric
    DataFrame-producing transform, so a preprocessing/decomposition step can be
    audited *directly* — the corpus gap is precisely that these transforms are fit
    on the whole sample in a step *outside* the model, which purge/embargo
    walk-forward does not catch. Require the entire pipeline (preprocessing
    included) to be ``transform_fn``: a transform fit train-only and applied
    causally per window is invariant under truncation; one fit on the full sample
    is not. (A stateful fit-once transform object needs isolation — see the core.)
    """
    return _whole_window_causal_check(
        transform_fn,
        data,
        name="causal_transform",
        leak_label="non-causal transform",
        min_history=min_history,
        max_cutoffs=max_cutoffs,
        atol=atol,
        rtol=rtol,
    )


def check_no_lookahead(
    signal_fn: Callable[[pd.DataFrame], pd.DataFrame],
    prices: pd.DataFrame,
    *,
    min_history: int = 30,
    max_cutoffs: int | None = None,
    atol: float = 1e-10,
    rtol: float = 1e-9,
) -> CheckResult:
    """Execute-and-compare lookahead detector.

    ``signal_fn`` maps a price panel to a weight panel on the same index. It is
    re-run on truncated histories and its **entire output** must equal the
    full-sample output over the overlap: a causal function's value at any date
    s <= t depends only on data up to s. Cutoffs are **exhaustive** (every row
    becomes a boundary once) so a finite-horizon leak (a 1-day lookahead is visible
    only at the boundary row) cannot dodge onto an evenly-spaced grid, and the
    most-recent rows are covered. See ``_whole_window_causal_check`` for the
    determinism pre-check, fail-closed coercion, and the isolation caveat.
    """
    return _whole_window_causal_check(
        signal_fn,
        prices,
        name="no_lookahead",
        leak_label="lookahead",
        min_history=min_history,
        max_cutoffs=max_cutoffs,
        atol=atol,
        rtol=rtol,
    )
