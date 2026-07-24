"""Equal-treatment protocol for a candidate-vs-null comparison — verifier item V2.

A candidate that "beats the null" only counts if the two arms were treated
identically: the SAME train/test split, the SAME preprocessing, and an EQUAL,
bounded hyperparameter budget (TFB p. 8; ts_forecasting_integration.md §4.1). A
better-tuned or differently-split candidate has an unfair advantage, so the
comparison cannot certify an edge.

Disposition is ``validation_pending`` for every failure (not ``reject``): an
unfair or un-instrumented comparison does not disqualify the *strategy* — it means
the *comparison* is unverifiable, so the result stays provisional until a fair
comparison is run (unverifiable ≠ rejected).

Anti-vacuous-pass: the gate FAILS CLOSED on any un-logged field. An
un-instrumented comparison (no split id / preprocessing id / budget) must never
pass — otherwise the gate is theater. Use ``treatment_fingerprint`` to derive the
ids from real content (split indices, preprocessing params) so equality is
meaningful rather than a free-text attestation.

Research-only: evaluates comparison metadata; it never acts.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from project_money.validation.invariants import CheckResult, VALIDATION_PENDING


def _finite_nonneg_int(x) -> bool:
    """True iff ``x`` is a finite, non-negative, integral *number*.

    Rejects ``None``, ``bool``, non-numeric types (e.g. the string ``"10"``),
    ``NaN``, ``inf``, negatives, and non-integers — the fail-closed guard for the
    hyperparameter budget and its tolerance. A non-finite or non-numeric budget is
    an *un-instrumented* comparison, not a zero one, so it must fail closed rather
    than slip through a naive ``<``/``>`` comparison (NaN defeats both — the
    S11/S16 NaN-fails-open lesson) or raise on a later subtraction."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    return math.isfinite(x) and x >= 0 and x == int(x)


def _item_digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def treatment_fingerprint(obj) -> str:
    """Order-invariant content hash of a split index or preprocessing descriptor.

    Deterministic across runs and processes (sha256, no salt), so two arms that
    used the same split / preprocessing produce the same id. Order-invariant (a
    train/test split is defined by its member SET, a param dict by its items), so
    row order does not spuriously differ. Raises on ``None`` — an un-attested arm
    must fail closed, never hash to a shared constant.

    Collision-safe by construction: each element is ``repr``-serialized (so ``1``
    and ``"1"`` differ) and hashed to a fixed-width digest *before* being combined,
    so no in-value delimiter can make two distinct contents collide. Fingerprint
    the held-out index or an explicit ``(train, test)`` partition — not a flat
    union of all rows — so two different partitions of the same rows differ.
    """
    if obj is None:
        raise ValueError("cannot fingerprint None — an un-attested arm must fail closed, not hash to a constant")
    if hasattr(obj, "tolist"):  # pandas Index/Series, numpy array
        obj = obj.tolist()
    if isinstance(obj, (list, tuple, set, frozenset, dict)) and len(obj) == 0:
        raise ValueError(
            "cannot fingerprint an empty collection — an empty split/descriptor is not instrumented "
            "(would hash to a shared constant); fail closed"
        )
    if isinstance(obj, dict):
        parts = sorted(_item_digest(f"{k!r}={obj[k]!r}") for k in obj)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        parts = sorted(_item_digest(repr(x)) for x in obj)
    else:
        parts = [_item_digest(repr(obj))]
    # Each part is a fixed-width hex digest, so concatenation is unambiguous.
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True)
class TreatmentRecord:
    """The comparison metadata for ONE arm (candidate or null). Any field left
    ``None`` fails V2 closed — an un-instrumented comparison must never pass.

    ``split_id`` / ``preprocessing_id`` should be content-derived (see
    ``treatment_fingerprint``); ``hp_budget`` is the count of hyperparameter
    configurations that arm was tuned over."""

    split_id: str | None = None
    preprocessing_id: str | None = None
    hp_budget: int | None = None


def check_equal_treatment(
    candidate: TreatmentRecord, null: TreatmentRecord, *, budget_tol: int = 0
) -> CheckResult:
    """Verify a candidate and its null/baseline got equal treatment (V2).

    Fails closed (``validation_pending``) if either arm did not log its split id,
    preprocessing id, or hp budget; if the splits or preprocessing differ; or if
    the hyperparameter budgets differ by more than ``budget_tol`` (or are
    negative). Passing means "the comparison was fair" — NOT that the candidate
    has an edge; compose with the edge-existence gates.
    """
    reasons: list[str] = []

    # 1. Fail closed on any un-logged attestation (the vacuous-pass guard).
    for arm_name, arm in (("candidate", candidate), ("null", null)):
        if arm.split_id is None:
            reasons.append(f"{arm_name} split id not logged — comparison not instrumented (fail closed)")
        if arm.preprocessing_id is None:
            reasons.append(f"{arm_name} preprocessing id not logged — comparison not instrumented (fail closed)")
        if arm.hp_budget is None:
            reasons.append(f"{arm_name} hyperparameter budget not logged — comparison not instrumented (fail closed)")
        elif not _finite_nonneg_int(arm.hp_budget):
            reasons.append(
                f"{arm_name} hyperparameter budget {arm.hp_budget!r} is not a finite non-negative integer — fail closed"
            )

    # 2. Identical split and preprocessing (only comparable when both arms logged them).
    if candidate.split_id is not None and null.split_id is not None and candidate.split_id != null.split_id:
        reasons.append(
            f"splits differ between candidate ({candidate.split_id}) and null ({null.split_id}) — "
            "not an equal-treatment comparison"
        )
    if (
        candidate.preprocessing_id is not None
        and null.preprocessing_id is not None
        and candidate.preprocessing_id != null.preprocessing_id
    ):
        reasons.append(
            f"preprocessing differs between candidate ({candidate.preprocessing_id}) and "
            f"null ({null.preprocessing_id}) — not an equal-treatment comparison"
        )

    # 3. Equal hyperparameter budget — only comparable when both budgets AND the
    #    tolerance are finite non-negative integers (a non-finite value must not
    #    disable the asymmetry check by defeating the `>` comparison).
    if _finite_nonneg_int(candidate.hp_budget) and _finite_nonneg_int(null.hp_budget):
        if not _finite_nonneg_int(budget_tol):
            reasons.append(f"budget_tol {budget_tol!r} is not a finite non-negative integer — fail closed")
        elif abs(candidate.hp_budget - null.hp_budget) > budget_tol:
            reasons.append(
                f"asymmetric hyperparameter budget (candidate {candidate.hp_budget} vs null {null.hp_budget}, "
                f"tol {budget_tol}) — the better-tuned arm has an unfair advantage"
            )

    return CheckResult("equal_treatment", not reasons, reasons, VALIDATION_PENDING)
