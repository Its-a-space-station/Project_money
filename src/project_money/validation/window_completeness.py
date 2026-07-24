"""Window-completeness assertion — verifier item V1 (anti-drop-last).

Backtest and forecast-evaluation code slides a fixed lookback+horizon window
across the test span and scores each window. A pervasive, silent bug — the
"drop-last" artifact documented in the TFB benchmark (Qiu et al., pp. 3, 9) — is
that the *last, incomplete* batch of windows is discarded (e.g. a data loader
with ``drop_last=True``, or a vectorized chunking that drops a remainder), so the
reported metric is computed over fewer windows than the declared geometry
implies. Because the dropped windows are not random, the reported number can move
— by as much as ~17% in TFB's measurement — purely as a function of an
*engineering* parameter (batch size, chunk size) that must have no bearing on a
scientific result.

This gate reconciles the *actual* number of scored windows against the count the
declared evaluation geometry implies, and — when given counts observed under more
than one engineering setting — asserts the count is invariant to them. A mismatch,
or any dependence on an engineering knob, hard-``reject``s: the reported metric
was computed over a different sample than it claims, so it cannot be trusted.

The declared geometry (``n_obs``, ``lookback``, ``horizon``, ``stride``) and any
explicit ``expected_windows`` are *pre-registration-load-bearing* facts about the
evaluation, not tunable knobs — each is validated (integer, in range) and, when
both a geometry and an explicit count are supplied, they are cross-checked for
internal consistency. The geometry assumes the standard sliding-window
convention (``expected_window_count``); an evaluation using a different windowing
convention declares its count via ``expected_windows`` instead. A declared
geometry that yields zero scored windows is itself a degenerate (nothing-tested)
evaluation and fails closed rather than passing vacuously.

Research-only: it audits an evaluation's bookkeeping; it never acts.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from project_money.validation.invariants import CheckResult


def expected_window_count(n_obs: int, lookback: int, horizon: int, stride: int = 1) -> int:
    """Number of sliding windows of a ``lookback``-input, ``horizon``-target shape
    that fully fit in ``n_obs`` observations, stepping by ``stride``.

    A window starting at position ``p`` consumes ``span = lookback + horizon``
    observations (input rows ``[p, p+lookback)`` then target rows
    ``[p+lookback, p+span)``), so ``p`` ranges over ``0, stride, 2*stride, ...``
    up to ``n_obs - span``; the count is ``floor((n_obs - span) / stride) + 1``,
    and 0 when a single window does not fit. This is the count a correct
    sliding-window evaluation scores and the count ``drop_last`` truncation
    violates. Inputs are assumed already validated (integer, in range).
    """
    span = lookback + horizon
    if n_obs < span:
        return 0
    return (n_obs - span) // stride + 1


def _int_at_least(value, label: str, minimum: int) -> str | None:
    """None if ``value`` is an integer >= ``minimum``, else a fail-closed reason.

    ``bool`` is an ``int`` subclass in Python; reject it explicitly — a window
    count is never a flag. ``numpy`` integer scalars are accepted; floats (even
    integral-valued like ``90.0``) and ``numpy.bool_`` are not."""
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        return f"{label} must be an integer >= {minimum}, got {value!r} — fail closed"
    if int(value) < minimum:
        return f"{label} must be an integer >= {minimum}, got {value!r} — fail closed"
    return None


def check_window_completeness(
    scored_windows,
    *,
    expected_windows=None,
    n_obs=None,
    lookback=None,
    horizon=None,
    stride: int = 1,
    engineering_counts: Mapping[str, int] | None = None,
) -> CheckResult:
    """Reconcile the number of scored evaluation windows against the declared
    geometry, and assert invariance to engineering-only parameters — verifier V1.

    Supply the expected count one of two ways (both may be given, and are then
    cross-checked for consistency):

    * ``expected_windows`` — the pre-registered count directly, or
    * ``n_obs`` + ``lookback`` + ``horizon`` (+ ``stride``, default 1) — the
      sliding-window geometry, from which the count is computed via
      ``expected_window_count``.

    ``engineering_counts`` maps a label (e.g. ``"batch_size=32"``) to the scored
    count observed under that engineering setting; every value must equal
    ``scored_windows`` (a count that moves with batch/chunk size is the drop-last
    fingerprint).

    **Scope (do not over-read a pass).** A pass certifies that ``scored_windows``
    matches the count implied by the *declared* geometry / ``expected_windows``,
    and (when supplied) that the count is identical across the given
    ``engineering_counts`` settings. It cannot detect a *lie* about the geometry
    or ``scored_windows`` — those are pre-registration-load-bearing declared facts
    (a candidate that both drops windows *and* declares a geometry matching the
    truncated count is out of scope for any count-reconciliation gate). And
    invariance to an engineering parameter is only *demonstrated* when
    ``engineering_counts`` carries at least one alternative setting; absent it, a
    pass means "matches the one declared geometry", not "proven invariant to
    batch/chunk". The honest drop-last case is still caught either way: a loader
    that keeps 64 of a declared 90 windows mismatches and rejects.

    Fails closed (``reject``) on: any malformed / out-of-range input; neither an
    explicit count nor a full geometry supplied; a geometry that internally
    disagrees with an explicit ``expected_windows``; a degenerate zero-window
    evaluation; ``scored_windows`` != expected (drop-last / miscount); or any
    engineering setting whose count differs. All failures carry the ``reject``
    disposition — a metric computed over the wrong window set is not a matter for
    review, it is untrustworthy by construction.
    """
    reasons: list[str] = []

    # --- validate the actual count and any engineering counts -----------------
    err = _int_at_least(scored_windows, "scored_windows", 0)
    if err:
        reasons.append(err)

    # ``stride`` is the gate's own knob — validate it unconditionally so an
    # out-of-range value is surfaced even when no geometry consumes it (and so a
    # bad stride can never reach the ``// stride`` in expected_window_count).
    stride_err = _int_at_least(stride, "stride", 1)
    if stride_err:
        reasons.append(stride_err)

    # Kept as a list of (label, count) pairs — NOT a dict keyed by str(label):
    # two distinct labels can share a str() (e.g. 32 and "32"), and re-keying
    # would silently drop one of the gate's own inputs (an order-dependent
    # fail-open of the invariance check). Every validated count is preserved.
    checked_eng: list[tuple[str, int]] = []
    if engineering_counts is not None:
        if not isinstance(engineering_counts, Mapping):
            reasons.append("engineering_counts must be a mapping {label: count} — fail closed")
        else:
            for label, count in engineering_counts.items():
                e = _int_at_least(count, f"engineering_counts[{label!r}]", 0)
                if e:
                    reasons.append(e)
                else:
                    checked_eng.append((str(label), int(count)))

    # --- resolve the expected count -------------------------------------------
    have_geometry = any(v is not None for v in (n_obs, lookback, horizon))
    geom_expected: int | None = None
    if have_geometry:
        if None in (n_obs, lookback, horizon):
            reasons.append(
                "partial geometry: n_obs, lookback and horizon must all be given together — fail closed"
            )
        else:
            geom_errs = [
                e
                for e in (
                    _int_at_least(n_obs, "n_obs", 0),
                    _int_at_least(lookback, "lookback", 0),
                    _int_at_least(horizon, "horizon", 1),
                )
                if e
            ]
            reasons.extend(geom_errs)
            # Compute only when the whole geometry AND stride are well-formed —
            # otherwise expected_window_count would divide by a bad stride.
            if not geom_errs and stride_err is None:
                geom_expected = expected_window_count(
                    int(n_obs), int(lookback), int(horizon), int(stride)
                )

    explicit_expected: int | None = None
    if expected_windows is not None:
        e = _int_at_least(expected_windows, "expected_windows", 0)
        if e:
            reasons.append(e)
        else:
            explicit_expected = int(expected_windows)

    if not have_geometry and expected_windows is None:
        reasons.append(
            "must supply either expected_windows or a full geometry (n_obs, lookback, horizon) "
            "— fail closed"
        )

    # Any validation problem → fail closed; never compute on bad inputs.
    if reasons:
        return CheckResult("window_completeness", False, reasons)

    # Both supplied → they must agree; a geometry that contradicts the declared
    # count is an internally inconsistent declaration.
    if (
        explicit_expected is not None
        and geom_expected is not None
        and explicit_expected != geom_expected
    ):
        return CheckResult(
            "window_completeness",
            False,
            [
                f"declared expected_windows={explicit_expected} disagrees with the geometry's "
                f"{geom_expected} (n_obs={n_obs}, lookback={lookback}, horizon={horizon}, "
                f"stride={stride}) — inconsistent declaration, fail closed"
            ],
        )

    expected = explicit_expected if explicit_expected is not None else geom_expected

    # A geometry (or declaration) that yields zero windows tested nothing.
    if expected == 0:
        return CheckResult(
            "window_completeness",
            False,
            [
                "declared geometry yields zero scored windows — the evaluation span is shorter than "
                "one lookback+horizon window; nothing was tested (vacuous), fail closed"
            ],
        )

    sw = int(scored_windows)
    if sw != expected:
        if sw < expected:
            reasons.append(
                f"scored {sw} windows but the declared geometry implies {expected} "
                f"({expected - sw} missing — drop-last / silent truncation fingerprint)"
            )
        else:
            reasons.append(
                f"scored {sw} windows but the declared geometry implies only {expected} "
                f"({sw - expected} extra — overlapping/double-counted windows or a mis-declared geometry)"
            )

    # Engineering-invariance: the count must not move with an engineering knob.
    for label, count in checked_eng:
        if count != sw:
            reasons.append(
                f"scored-window count depends on an engineering parameter: {label} -> {count} "
                f"vs the reported {sw} — a scientific result must not vary with batch/chunk size"
            )

    return CheckResult("window_completeness", not reasons, reasons)
