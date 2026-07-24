"""Effect-size gate — verifier item V4 (economic magnitude beside significance).

A p-value or a deflated-Sharpe verdict answers "is this effect distinguishable
from zero?" — never "is it big enough to matter?" With enough data a trivially
small edge clears any significance bar, so a backtest that is *statistically*
significant but *economically* negligible is a classic false discovery of
tradeable value: capital gets deployed on an edge smaller than the cost to harvest
it. (QuitoBench p. 27.)

This gate enforces the reporting discipline that every significance claim carries a
declared effect size — an economic magnitude (annualized net edge, information
coefficient, Cohen's d, ...) — and routes a *significant* result whose effect is
below a pre-registered materiality threshold to human adjudication
(``needs_human_review``) rather than letting it promote as an edge. It is the
lightweight companion to the full Bayesian ROPE gate (the batch-3 item:
``p(|Δ| > ε | D)`` from a Student-t posterior on paired per-fold results); V4 needs
only the point effect size and the significance verdict, whereas ROPE needs the
per-fold distribution.

**Scope (one axis, necessary-not-sufficient).** Like S11/S16 this is a one-sided
review alarm, not an edge screen: a *pass* means "not significant, or significant
AND materially large" — never "has a validated edge". It MUST be composed with the
edge-existence gates (deflated Sharpe / multiplicity, no-lookahead, the
falsification battery). Orient ``effect_size`` so that larger = better edge; for an
inherently two-sided effect (direction not meaningful) pass its magnitude.

Research-only: it evaluates a reported magnitude; it never acts.
"""

from __future__ import annotations

import math

import numpy as np

from project_money.validation.invariants import (
    CheckResult,
    NEEDS_HUMAN_REVIEW,
    VALIDATION_PENDING,
)


def _finite_float(x) -> float | None:
    """``float(x)`` if finite, else None.

    Returns None (fail-closed) for None, NaN, inf, non-numeric, and over-large ints
    (``float(10**400)`` raises ``OverflowError`` — a Stage-0 check must never raise).
    Stringly-typed inputs are rejected *before* coercion: a load-bearing magnitude /
    threshold must arrive as a real number, not a string/bytes that merely parses
    (consistent with the strict ``significant`` typing; ``Decimal`` / ``Fraction`` /
    numpy numeric scalars are still accepted). This covers numpy string/bytes
    scalars and 0-d arrays too (dtype kind ``U``/``S``), which are not Python
    ``str``/``bytes`` instances but must fail closed the same way."""
    if isinstance(x, (str, bytes, bytearray)):
        return None
    dtype = getattr(x, "dtype", None)  # numpy string/bytes (kind U/S) — numeric kinds pass
    if dtype is not None and getattr(dtype, "kind", None) in ("U", "S"):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError, OverflowError):
        return None
    return v if math.isfinite(v) else None


def _short(x) -> str:
    """Bounded repr of a possibly candidate-authored value for a reason string —
    truncated so an untrusted input cannot plant unbounded text into ``reasons``
    (which flow to the ledger and, per the corpus, potentially to an LLM judge). A
    safety-stringify helper must not itself be a crash surface, so a value whose
    ``__repr__`` raises degrades to a placeholder rather than propagating."""
    try:
        return repr(x)[:80]
    except Exception:
        return "<unrepresentable>"


def check_effect_size(
    effect_size,
    *,
    min_effect,
    significant: bool = True,
    effect_name: str = "effect size",
) -> CheckResult:
    """Flag a statistically significant result whose economic magnitude is below a
    pre-registered materiality threshold — verifier V4.

    Parameters
    ----------
    effect_size:
        The declared economic magnitude of the result, oriented so larger = better
        edge (for a two-sided effect, pass its magnitude). Missing / non-finite
        while a significance claim is made → ``validation_pending`` (the magnitude
        was not declared, so economic significance cannot be certified).
    min_effect:
        The pre-registered materiality threshold (same scale as ``effect_size``),
        strictly positive and finite. It is the gate's own knob — a non-positive /
        non-finite bar makes the gate vacuous and hard-``reject``s (fail closed).
    significant:
        The upstream significance verdict (p / deflated-Sharpe), a genuine bool.
        ``False`` short-circuits to a pass — V4 only guards the
        significant-but-immaterial trap; the significance / DSR gate owns the
        rejection of non-significant results. (On that abstain path the materiality
        knob is not consulted, so V4 does not police a mis-registered ``min_effect``
        for a non-significant candidate — not its contract.) A non-bool fails closed
        (``reject``).
    effect_name:
        A *trusted constant* label interpolated into the reason string (defensively
        truncated); never source it from candidate-authored metadata.

    Dispositions: ``reject`` for a broken knob / malformed verdict (fail-closed);
    ``validation_pending`` for a significance claim with no usable effect size;
    ``needs_human_review`` for a significant-but-sub-material effect (negligible
    magnitude, or a materially adverse / negative sign). A pass carries no
    disposition (empty reasons).
    """
    name = "effect_size"

    # The significance verdict must be a real boolean, not a truthy proxy.
    if not isinstance(significant, (bool, np.bool_)):
        return CheckResult(
            name,
            False,
            [f"significant {_short(significant)} must be a bool (the upstream significance "
             "verdict) — fail closed"],
        )

    # A non-significant result is out of V4's scope — the significance / DSR gate
    # owns that rejection; V4 only guards the significant-but-immaterial trap.
    if not bool(significant):
        return CheckResult(name, True, [])

    # The gate's own knob: a non-positive / non-finite materiality bar is vacuous.
    me = _finite_float(min_effect)
    if me is None or me <= 0.0:
        return CheckResult(
            name,
            False,
            [f"min_effect {_short(min_effect)} must be a positive, finite materiality threshold — "
             "fail closed (a non-positive / non-finite bar makes the gate vacuous)"],
        )

    # A significance claim without a declared, usable effect size cannot be
    # certified for economic magnitude → validation_pending (the V4 mandate:
    # every significance claim carries an effect size).
    es = _finite_float(effect_size)
    if es is None:
        return CheckResult(
            name,
            False,
            [f"{str(effect_name)[:80]} {_short(effect_size)} is missing / non-finite — a significance "
             "claim must declare a usable effect size (economic magnitude); cannot certify"],
            VALIDATION_PENDING,
        )

    if es >= me:
        return CheckResult(name, True, [])  # significant AND materially large — pass

    # Significant but sub-material: negligible magnitude, or a material adverse sign.
    if es < 0.0:
        reason = (
            f"statistically significant but {str(effect_name)[:80]} = {es:.6g} is NEGATIVE "
            f"(adverse direction; materiality bar {me:.6g}) — a reliably wrong-direction result "
            "must not be promoted as an edge without human adjudication"
        )
    else:
        reason = (
            f"statistically significant but {str(effect_name)[:80]} = {es:.6g} is below the "
            f"pre-registered material threshold {me:.6g} — economically negligible; do not promote "
            "as a tradeable edge without human adjudication"
        )
    return CheckResult(name, False, [reason], NEEDS_HUMAN_REVIEW)
