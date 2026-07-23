"""Intra-bar contemporaneous-leakage detector — verifier item S6.

The single highest-value gap the batch-6 corpus exposed (stock_market_synthesis
§6.1): a leak that lives *inside* one bar and is therefore invisible to any
date-granularity lookahead check. The motivating specimen is Mehtab & Sen
"Case III" — 94.76% reported out-of-sample directional accuracy produced by
using a bar's own high/low/close to predict a quantity that is *decided* at that
bar's open. A walk-forward / purge-embargo test passes it (feature and target
share the same timestamp t); the leak is sub-bar, in the information-*arrival
order* within the bar — the open prints first, while high/low (and the bar's
final close and volume) are only known once the bar has traded through.

Detector philosophy mirrors ``check_no_lookahead``: do not trust a claim of
causality — execute it. A signal committed at a stated decision point of bar t
must be invariant to any bar-t field that only becomes known *after* that point.
We perturb exactly those not-yet-available fields (holding the decision-time
fields and every other bar fixed) and require the signal at t not to move — in
value, sign, or NaN-definedness.

**Purity precondition (load-bearing).** Like every execute-and-compare check
(including ``check_no_lookahead``), this gate assumes ``signal_fn`` is a *pure*
function of its input. A stateful/memoized ``signal_fn`` can defeat the core
comparison by returning a cached value instead of recomputing. The
``check_statefulness`` cold-reindex probe catches the common **recompute-on-miss**
(index/date-keyed) cache, and — via a cold-**no**-perturb baseline — does so
WITHOUT false-flagging legitimate calendar/seasonality signals (whose output
legitimately depends on the index; a core quant strategy family). It does NOT
catch a **compute-once / constant-return** cache (``base`` itself is the leaked
answer, reproduced forever, so no compare-to-``base`` probe can see it) or other
fully adversarial statefulness; certifying those requires process/object
isolation, tracked as verification debt — not silently ignored.

Hardened over two adversarial red-team rounds (exploits kept as regression
specimens in ``tests/specimens.py``):

* **Exhaustive positions** by default — no recomputable grid to game (FN-1). The
  ``max_test_bars`` fast path is a best-effort screen only (its selection is
  data-derived but in principle recomputable); exhaustive is the trustworthy mode.
* **Wide, vol-scaled perturbation set** spanning the instrument's realized range
  in both directions and beyond (FN-2), always applied in full.
* **Sign / NaN-aware comparison at a tight absolute tolerance** — no ``rtol``
  scaled by |value| (a DC offset would inflate that budget; FN-3). A truly causal
  signal is bit-identical under perturbation of untouched fields, so any change
  beyond ``atol`` — including a sign flip — is a leak.
* **Determinism pre-check** (FP-1) and **fail-closed coercion** (R-1).
* **Cold-reindex statefulness probe** (round-2/3 memoization) — catches
  recompute-on-miss caches; a cold-no-perturb baseline first separates legitimate
  calendar/seasonality dependence (not flagged) from position-based memoization.
* **Absolute volume probes** (round-3) — including a zero probe, so a leak keyed
  on a zero-volume bar (which multiplicative probes cannot move) is exercised.

``decision_at="close"``: the whole bar is known at the close, so nothing arrives
afterward and this check is vacuously satisfied — it gives S6 *no* coverage for
close-committed signals; that coverage is ``check_no_lookahead``'s job.

Research-only: this evaluates an artifact; it never acts.
"""

from __future__ import annotations

import hashlib
from typing import Callable

import numpy as np
import pandas as pd

from project_money.validation.invariants import CheckResult

OHLC_COLUMNS = ("open", "high", "low", "close")

# Information-arrival order *within* a single bar. The open prints first; the
# high and low are only known once the bar has traded through them; the close
# (and the bar's settled volume) are known only at the bar's end. Equal ranks
# are treated as arriving together.
_ARRIVAL_ORDER: dict[str, int] = {
    "open": 0,
    "high": 1,
    "low": 1,
    "close": 2,
    "volume": 2,
}

SignalFn = Callable[[pd.DataFrame], "pd.Series | pd.DataFrame"]


def _as_matrix(out: "pd.Series | pd.DataFrame", index: pd.Index) -> np.ndarray | None:
    """Coerce a signal output to a 2-D float matrix aligned to ``index``.

    Returns ``None`` on any structural fault — index mismatch or non-numeric
    values — so the caller fails closed rather than crashing or passing.
    """
    if isinstance(out, pd.Series):
        out = out.to_frame()
    if not isinstance(out, pd.DataFrame) or not out.index.equals(index):
        return None
    try:
        return out.to_numpy(dtype=float)
    except (ValueError, TypeError):
        return None


def _matrices_equal(a: np.ndarray, b: np.ndarray, *, atol: float) -> bool:
    """NaN-aware equality for two aligned matrices (for the determinism check)."""
    nan_a, nan_b = np.isnan(a), np.isnan(b)
    if not np.array_equal(nan_a, nan_b):
        return False
    valid = ~nan_a
    return not valid.any() or bool(np.all(np.abs(a[valid] - b[valid]) <= atol))


def _row_change(base_row: np.ndarray, pert_row: np.ndarray, *, atol: float) -> str | None:
    """Classify how a signal row changed under perturbation, or ``None`` if it did
    not. A truly causal signal is bit-identical when fields it does not use are
    perturbed, so the tolerance is a tight *absolute* value — no ``rtol`` scaled
    by |value|, which a DC offset would inflate. Detects NaN-definedness change,
    sign flip (scale-invariant — the way leaks are consumed downstream), and any
    value move beyond ``atol``."""
    nan_b, nan_p = np.isnan(base_row), np.isnan(pert_row)
    if not np.array_equal(nan_b, nan_p):
        return "NaN-definedness"
    valid = ~nan_b
    if not valid.any():
        return None
    b, p = base_row[valid], pert_row[valid]
    if np.any(np.sign(b) != np.sign(p)):
        return "sign"
    if np.any(np.abs(b - p) > atol):
        return "value"
    return None


def _price_deltas(bars: pd.DataFrame) -> list[float]:
    """Relative close moves to probe: a wide fixed spread plus the instrument's
    own realized min/max intraday move (so the probe is vol-scaled and spans the
    field's plausible domain in both directions). Clipped above -1 (prices > 0)."""
    ratios = (bars["close"] / bars["open"] - 1.0).replace([np.inf, -np.inf], np.nan).dropna()
    r_lo = float(ratios.min()) if not ratios.empty else -0.1
    r_hi = float(ratios.max()) if not ratios.empty else 0.1
    candidates = {-0.5, -0.15, -0.05, 0.05, 0.15, 0.5, r_lo - 0.05, r_hi + 0.05}
    return sorted(d for d in candidates if d > -0.99)


def _test_positions(
    bars: pd.DataFrame, *, min_history: int, max_test_bars: int | None
) -> np.ndarray:
    """Bars to probe. Exhaustive by default (no recomputable grid to game); above
    ``max_test_bars`` a best-effort selection — data-driven extremes (where leaks
    concentrate) plus a data-digest-seeded random sample (deterministic and
    reproducible, not a fixed public grid). NOTE this fast path is a screen, not a
    guarantee: its selection is in principle recomputable, so exhaustive (the
    default) is the trustworthy mode. Tracked as verification debt."""
    usable = np.arange(min_history, len(bars))
    if len(usable) == 0 or max_test_bars is None or len(usable) <= max_test_bars:
        return usable

    o = bars["open"].to_numpy(dtype=float)
    c = bars["close"].to_numpy(dtype=float)
    hi = bars["high"].to_numpy(dtype=float)
    lo = bars["low"].to_numpy(dtype=float)
    move = np.abs(np.divide(c - o, o, out=np.zeros_like(o), where=o != 0))
    rng_ = np.abs(np.divide(hi - lo, o, out=np.zeros_like(o), where=o != 0))
    vol = bars["volume"].to_numpy(dtype=float) if "volume" in bars.columns else np.zeros_like(o)
    score = move + rng_ + (vol / (np.median(vol) + 1.0) if vol.any() else 0.0)

    seed = int.from_bytes(
        hashlib.sha256(bars[list(OHLC_COLUMNS)].to_numpy(dtype=float).tobytes()).digest()[:8],
        "little",
    )
    rng = np.random.default_rng(seed)
    half = max_test_bars // 2
    ranked = usable[np.argsort(score[usable])[::-1][:half]]
    sample = rng.choice(usable, size=min(max_test_bars - half, len(usable)), replace=False)
    return np.unique(np.concatenate([ranked, sample]))


def _cold_reindex(index: pd.Index, salt: int = 0) -> pd.Index:
    """A same-length index disjoint from ``index`` (and distinct per ``salt``) — so
    an index-keyed cache in a stateful signal_fn is cold and must recompute. A
    fresh ``salt`` per probe call is essential: reusing one cold index lets a
    memoizer cache the first call and return stale values for the next. Shifts a
    DatetimeIndex by a weekday-preserving amount beyond the panel; falls back to a
    far-offset RangeIndex."""
    n = len(index)
    if isinstance(index, pd.DatetimeIndex):
        freq = index.freq or pd.infer_freq(index)
        if freq is not None:
            shift_n = 5 * (n // 5 + 300 + 50 * salt)  # multiple of 5 preserves weekday
            try:
                shifted = index.shift(shift_n, freq=freq)
                if shifted.intersection(index).empty:
                    return shifted
            except (ValueError, TypeError):
                pass
    base = 1_000_000_000 + salt * (n + 1)
    return pd.RangeIndex(base, base + n)


def _statefulness_probe(
    signal_fn: SignalFn,
    bars: pd.DataFrame,
    base: np.ndarray,
    *,
    perturb_fields: list[str],
    col_idx: dict[str, int],
    positions: np.ndarray,
    deltas: list[float],
    med_vol: float,
    atol: float,
) -> str | None:
    """Catch the recompute-on-miss (index/date-keyed) memoization bypass without
    false-flagging legitimate calendar/seasonality signals.

    Step 1 — classify: run ``signal_fn`` on a cold-reindexed copy with the data
    *unperturbed* and compare to ``base``. If it differs, the output legitimately
    depends on the index (calendar/seasonality, or index-keyed in a way we cannot
    distinguish from calendar) — the cold-reindex probe is inapplicable, so we do
    NOT flag. Step 2 — only for position-based signals (cold-no-perturb == base):
    perturb a few bars' post-decision fields on *further, distinct* cold indices
    (so a recompute-on-miss cache must recompute); any positional divergence there
    is perturbation-driven → a real recompute leak.

    Does not catch compute-once/constant caches (``base`` is itself the cached
    answer) — those need isolation (verification debt)."""
    # Step 1: cold-no-perturb baseline (salt 1) — separates calendar-dependence.
    cold_bars = bars.set_axis(_cold_reindex(bars.index, 1), axis=0).copy()
    cold_base = _as_matrix(signal_fn(cold_bars), cold_bars.index)
    if cold_base is None or not _matrices_equal(base, cold_base, atol=atol):
        # inapplicable (can't classify) or legitimately index/calendar-dependent.
        return None

    # Step 2: position-based → perturbation-driven divergence is a real leak.
    probe_idx = positions[np.linspace(0, len(positions) - 1, min(5, len(positions)), dtype=int)]
    salt = 1
    for pos in np.unique(probe_idx):
        open_px = float(bars["open"].iat[pos])
        for d in (deltas[0], deltas[-1]):
            salt += 1  # distinct cold index per call — a recompute-on-miss cache stays cold
            work = bars.set_axis(_cold_reindex(bars.index, salt), axis=0).copy()
            close_px = open_px * (1.0 + d)
            new_vals = {
                "close": close_px,
                "high": max(open_px, close_px) * 1.001,
                "low": min(open_px, close_px) * 0.999,
                "volume": med_vol,
            }
            for c in perturb_fields:
                work.iat[pos, col_idx[c]] = new_vals[c]
            out = _as_matrix(signal_fn(work), work.index)
            if out is None or _row_change(base[pos], out[pos], atol=atol) is not None:
                return (
                    f"bar {bars.index[pos]}: output changed under a cold-reindex + perturbation "
                    "probe on a position-based signal — signal_fn appears stateful/impure "
                    "(date-keyed recompute-on-miss cache); execute-and-compare cannot certify "
                    "causality (confirm purity or run under isolation)"
                )
    return None


def check_intrabar_causality(
    signal_fn: SignalFn,
    bars: pd.DataFrame,
    *,
    decision_at: str = "open",
    min_history: int = 30,
    max_test_bars: int | None = None,
    atol: float = 1e-12,
    check_statefulness: bool = True,
) -> CheckResult:
    """Execute-and-compare intra-bar contemporaneous-leakage detector (S6).

    ``signal_fn`` maps an OHLC(V) bar panel to a per-bar signal (Series, or
    DataFrame on the same index). ``decision_at`` names when the signal is
    committed: ``"open"`` (only the open of bar t is known) or ``"close"`` (whole
    bar known → vacuously satisfied). See the module docstring for the purity
    precondition. Deterministic by construction; ``signal_fn`` must itself be
    deterministic (checked) and pure (probed).
    """
    reasons: list[str] = []

    missing = [c for c in OHLC_COLUMNS if c not in bars.columns]
    if missing:
        return CheckResult("intrabar_causality", False, [f"bars missing OHLC columns: {missing}"])
    if decision_at not in _ARRIVAL_ORDER:
        return CheckResult(
            "intrabar_causality",
            False,
            [f"decision_at={decision_at!r} not one of {sorted(_ARRIVAL_ORDER)}"],
        )

    decision_order = _ARRIVAL_ORDER[decision_at]
    perturb_fields = [
        c
        for c in ("high", "low", "close", "volume")
        if c in bars.columns and _ARRIVAL_ORDER[c] > decision_order
    ]
    if not perturb_fields:
        # Nothing in the bar arrives after the decision point → no channel for
        # contemporaneous leakage (e.g. decision_at="close").
        return CheckResult("intrabar_causality", True, [])

    # Determinism pre-check: a nondeterministic signal is its own failure.
    base = _as_matrix(signal_fn(bars), bars.index)
    if base is None:
        return CheckResult(
            "intrabar_causality",
            False,
            ["signal_fn output does not align with bars index (index mismatch or non-numeric)"],
        )
    base2 = _as_matrix(signal_fn(bars), bars.index)
    if base2 is None or not _matrices_equal(base, base2, atol=atol):
        return CheckResult(
            "intrabar_causality",
            False,
            ["signal_fn is nondeterministic (two runs on identical bars differ) — "
             "cannot audit causality; make it deterministic (DS2)"],
        )

    positions = _test_positions(bars, min_history=min_history, max_test_bars=max_test_bars)
    if len(positions) == 0:
        return CheckResult("intrabar_causality", False, ["not enough history for bar testing"])

    col_idx = {c: bars.columns.get_loc(c) for c in perturb_fields}
    deltas = _price_deltas(bars)
    # Absolute volume probes (round-3): include a zero and values spanning the
    # panel's scale, so a leak on a zero-volume bar (which a multiplicative probe
    # cannot move) is exercised, and zero<->nonzero transitions are tested.
    med_vol = float(np.median(bars["volume"])) if "volume" in bars.columns else 0.0
    med_vol = med_vol if med_vol > 0 else 1.0
    volume_probes = (0.0, med_vol, 2.0 * med_vol, 10.0 * med_vol)
    work = bars.copy()

    for pos in positions:
        t = bars.index[pos]
        open_px = float(bars["open"].iat[pos])
        base_row = base[pos]
        orig = {c: bars.iat[pos, col_idx[c]] for c in perturb_fields}

        scenarios: list[dict[str, float]] = []
        for d in deltas:  # move the linked price group together
            close_px = open_px * (1.0 + d)
            scenarios.append(
                {
                    "close": close_px,
                    "high": max(open_px, close_px) * 1.001,
                    "low": min(open_px, close_px) * 0.999,
                }
            )
        for v in volume_probes:  # probe volume independently across its scale
            scenarios.append({"volume": v})

        leak_reason: str | None = None
        for scenario in scenarios:
            touched = [c for c in scenario if c in perturb_fields]
            if not touched:
                continue
            for c in touched:
                work.iat[pos, col_idx[c]] = scenario[c]
            pert = _as_matrix(signal_fn(work), bars.index)
            for c in touched:  # restore before evaluating / next scenario
                work.iat[pos, col_idx[c]] = orig[c]

            if pert is None:
                leak_reason = "signal_fn output stopped aligning under perturbation"
                break
            change = _row_change(base_row, pert[pos], atol=atol)
            if change is not None:
                leak_reason = (
                    f"signal changed ({change}) when post-decision field(s) {touched} of the "
                    f"same bar were perturbed — intra-bar contemporaneous leakage "
                    f"(decision_at={decision_at})"
                )
                break

        if leak_reason is not None:
            reasons.append(f"bar {t}: {leak_reason}")

    # Only run the (more expensive, calendar-sensitive) statefulness probe if the
    # direct test found nothing — it exists to catch memoizers that the direct
    # test's same-index perturbation cannot, and to flag them distinctly.
    if not reasons and check_statefulness:
        stateful = _statefulness_probe(
            signal_fn,
            bars,
            base,
            perturb_fields=perturb_fields,
            col_idx=col_idx,
            positions=positions,
            deltas=deltas,
            med_vol=med_vol,
            atol=atol,
        )
        if stateful is not None:
            reasons.append(stateful)

    return CheckResult("intrabar_causality", not reasons, reasons)
