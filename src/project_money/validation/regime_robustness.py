"""Macro/micro dual aggregation — verifier item V5.

QuitoBench §2.2: a pooled (micro-average) metric can clear a bar purely because a
majority regime dominates, while the strategy fails in minority regimes. V5 reports
pooled AND per-regime results and flags a candidate that passes only the pooled
number — a prevalence-skew / majority-regime-specialist guard.

Disposition ``needs_human_review``, not ``reject``: a regime-conditional edge may
be REAL (tradeable in that regime only), so a human adjudicates rather than the gate
killing a possible winner. Necessary-not-sufficient — composes with the
edge-existence gates (deflated Sharpe, no-lookahead).

ALL of V5's knobs are pre-registration-load-bearing, not just ``regimes``: the
segmentation, ``bar``, ``higher_is_better``, ``min_regime_n``, and ``min_coverage``
must be fixed BEFORE seeing results, or a non-robust result can be laundered to a
pass (raise ``min_regime_n`` to exclude an inconvenient failing regime; lower
``min_coverage`` to disable the backstop; pick a single all-encompassing regime).
The gate validates these knobs are well-formed but cannot enforce that they were
pre-registered — that is a process control.

A regime with fewer than ``min_regime_n`` observations is not individually judged;
if the observations in judgeable regimes cover less than ``min_coverage`` of the
data, a cleared pooled edge is ``validation_pending`` (robustness unverifiable),
not a pass. Residual blind spot (verification debt): a strategy that fails only in
regimes each smaller than ``min_regime_n`` — up to ``(1 - min_coverage)`` of the
data — is not caught here; compose with the edge-existence gates.

Research-only: evaluates artifacts; it never acts.
"""

from __future__ import annotations

import math
from typing import Callable

import numpy as np

from project_money.validation.invariants import CheckResult, NEEDS_HUMAN_REVIEW, VALIDATION_PENDING

_MIN_TOTAL = 20


def _is_finite_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def check_regime_robustness(
    values,
    regimes,
    *,
    metric_fn: Callable[[np.ndarray], float],
    bar: float,
    higher_is_better: bool = True,
    min_regime_n: int = 30,
    min_coverage: float = 0.8,
) -> CheckResult:
    """Flag a pooled edge that is not robust across pre-registered regimes (V5).

    ``values`` is a per-observation metric input (returns, correct/incorrect flags,
    …); ``regimes`` is a same-length array of pre-registered regime labels;
    ``metric_fn`` maps a subset of ``values`` to a scalar; ``bar`` is the threshold
    (cleared when ``metric >= bar`` if ``higher_is_better`` else ``metric <= bar``).

    Outcomes: fail-closed ``reject`` on malformed input or a non-finite pooled
    metric; pass (nothing to distrust) when the pooled metric does not clear the
    bar; ``validation_pending`` when a cleared pooled edge is corroborated over less
    than ``min_coverage`` of the data; ``needs_human_review`` when a judgeable
    regime does not clear the bar though the pooled metric does.
    """
    # Config knobs are pre-registration-load-bearing (see module docstring) — a
    # non-finite bar or a disabled coverage floor would launder a non-robust pass.
    if not _is_finite_number(bar):
        return CheckResult("regime_robustness", False, [f"bar {bar!r} is not a finite number — fail closed"])
    if not (isinstance(min_regime_n, int) and not isinstance(min_regime_n, bool) and min_regime_n >= 1):
        return CheckResult(
            "regime_robustness", False, [f"min_regime_n {min_regime_n!r} must be an integer >= 1 — fail closed"]
        )
    if not (_is_finite_number(min_coverage) and 0.0 < min_coverage <= 1.0):
        return CheckResult(
            "regime_robustness", False, [f"min_coverage {min_coverage!r} must be in (0, 1] — fail closed"]
        )

    v = np.asarray(values, dtype=float).ravel()
    r = np.asarray(regimes).ravel()
    if len(v) != len(r):
        return CheckResult(
            "regime_robustness", False, [f"values/regimes length mismatch ({len(v)} vs {len(r)}) — fail closed"]
        )
    if len(v) < _MIN_TOTAL:
        return CheckResult(
            "regime_robustness", False, [f"insufficient total sample ({len(v)} < {_MIN_TOTAL}) — fail closed"]
        )
    finite = np.isfinite(v)  # drop NaN AND inf — a non-finite value must not survive into a regime metric
    v, r = v[finite], r[finite]
    if len(v) < _MIN_TOTAL:
        return CheckResult(
            "regime_robustness", False, [f"insufficient finite sample ({len(v)} < {_MIN_TOTAL}) — fail closed"]
        )

    def clears(m: float) -> bool:
        return math.isfinite(m) and (m >= bar if higher_is_better else m <= bar)

    micro = float(metric_fn(v))
    if not math.isfinite(micro):
        return CheckResult("regime_robustness", False, ["pooled (micro) metric is non-finite — fail closed"])
    if not clears(micro):
        # No pooled edge to distrust — V5 is necessary-not-sufficient.
        return CheckResult("regime_robustness", True, [])

    # Pooled clears — corroborate against each pre-registered regime large enough to judge.
    judgeable: dict = {}
    judged_n = 0
    for key in sorted(set(r.tolist()), key=str):
        sub = v[r == key]
        if len(sub) >= min_regime_n:
            judgeable[key] = float(metric_fn(sub))
            judged_n += len(sub)

    macro = float(np.mean(list(judgeable.values()))) if judgeable else float("nan")
    skew = [
        f"regime {key!r} (metric {m:.4g}) does not clear the bar {bar:.4g} while the pooled "
        f"micro-average {micro:.4g} does (macro-average {macro:.4g}) — possible majority-regime "
        "specialist (prevalence skew); a human must judge whether this is a real regime-conditional edge"
        for key, m in judgeable.items()
        if not clears(m)
    ]
    if skew:
        return CheckResult("regime_robustness", False, skew, NEEDS_HUMAN_REVIEW)

    coverage = judged_n / len(v)
    if coverage < min_coverage:
        return CheckResult(
            "regime_robustness",
            False,
            [f"a cleared pooled edge ({micro:.4g}) is corroborated over only {coverage:.0%} of observations "
             f"(regimes with >= {min_regime_n} obs; < {min_coverage:.0%}) — robustness unverifiable for the rest"],
            VALIDATION_PENDING,
        )
    return CheckResult("regime_robustness", True, [])
