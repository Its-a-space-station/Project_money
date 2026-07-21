"""Falsification harness: bracket tests, nuisance sweeps, differential
validation of fixes.

Terminal-Bench's oracle/dummy bracketing + the coffee automaton's differential
repair rule, as reusable checks for our own gates and metrics:

- a gate must PASS a known-true oracle case and FAIL a known-garbage case,
  or the gate itself is broken (bracket test);
- a metric whose value tracks a nuisance parameter (bin count, window length,
  threshold) is measuring the nuisance, not the phenomenon (sweep);
- a fix must zero the negative control while preserving the positive case
  (differential validation) — a fix that kills both is over-smoothing, one
  that kills neither isn't a fix.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

import numpy as np


def bracket_test(
    gate_fn: Callable[[Any], bool],
    oracle_case: Any,
    garbage_case: Any,
) -> dict[str, bool]:
    """A gate is trustworthy only if it separates a known-true case from a
    known-garbage case. Returns per-leg outcomes plus the joint verdict."""
    oracle_passes = bool(gate_fn(oracle_case))
    garbage_fails = not bool(gate_fn(garbage_case))
    return {
        "oracle_passes": oracle_passes,
        "garbage_fails": garbage_fails,
        "gate_trustworthy": oracle_passes and garbage_fails,
    }


def nuisance_sweep(
    metric_fn: Callable[..., float],
    data: Any,
    nuisance_grid: dict[str, Iterable[Any]],
) -> dict[str, dict[str, float]]:
    """Sweep each nuisance parameter independently (others at their first grid
    value) and report the metric's spread per parameter.

    A metric whose range across a nuisance sweep is comparable to its claimed
    signal is an artifact carrier for that nuisance. The caller judges against
    their effect size; this function only measures.
    """
    defaults = {k: list(v)[0] for k, v in nuisance_grid.items()}
    out: dict[str, dict[str, float]] = {}
    for name, values in nuisance_grid.items():
        vals = []
        for v in values:
            kwargs = dict(defaults)
            kwargs[name] = v
            vals.append(float(metric_fn(data, **kwargs)))
        arr = np.array(vals)
        out[name] = {
            "min": float(arr.min()),
            "max": float(arr.max()),
            "range": float(arr.max() - arr.min()),
            "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        }
    return out


def differential_validation(
    metric_fn: Callable[[Any], float],
    fixed_metric_fn: Callable[[Any], float],
    control_case: Any,
    signal_case: Any,
    *,
    control_tolerance: float,
    min_signal_retention: float = 0.5,
) -> dict[str, Any]:
    """Validate a metric fix differentially.

    The fix is accepted only if (a) on the known-zero control its |value| falls
    to ``control_tolerance`` or below, and (b) on the positive case it retains
    at least ``min_signal_retention`` of the original metric's value.
    """
    before_control = float(metric_fn(control_case))
    after_control = float(fixed_metric_fn(control_case))
    before_signal = float(metric_fn(signal_case))
    after_signal = float(fixed_metric_fn(signal_case))

    control_zeroed = abs(after_control) <= control_tolerance
    signal_retained = (
        abs(after_signal) >= min_signal_retention * abs(before_signal)
        if before_signal != 0
        else False
    )
    return {
        "before_control": before_control,
        "after_control": after_control,
        "before_signal": before_signal,
        "after_signal": after_signal,
        "control_zeroed": control_zeroed,
        "signal_retained": signal_retained,
        "fix_accepted": control_zeroed and signal_retained,
    }
