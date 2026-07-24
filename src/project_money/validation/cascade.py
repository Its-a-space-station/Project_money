"""Staged evaluation cascade with an explicit, published promotion policy.

The cost governor and junk filter (DGM's 10→60→200 gates; AlphaEvolve's
hypothesis-testing cascade; synthesis §4 tool 1): cheap deterministic screens
run first, expensive evaluation is reserved for survivors, every stage's
verdict and evidence are recorded, and a failure is never silently dropped —
the cascade result names the failing stage and its reasons (verification-debt
doctrine).

Stages are plain callables returning a ``(passed, metrics, reasons)`` triple, or
a ``(passed, metrics, reasons, disposition)`` quadruple when a failure is softer
than a hard reject, so the cascade is generic over what is being evaluated.
Thresholds live in the stage definitions — config, not vibes.

Failure disposition & label precedence. A failing stage's disposition is one of
(most→least severe):

  * ``reject`` (default) — hard disqualification.
  * ``validation_pending`` — the check ran but could not certify (e.g. an unfair
    or un-instrumented candidate-vs-null comparison); unverifiable ≠ rejected.
  * ``needs_human_review`` — a substantive concern a human must adjudicate (e.g.
    an implausibly high accuracy, a strong-but-plausible returns edge).

So a softer failure can never *mask* a harder one, the terminal label is:

  * the first stage that hard-``reject``s → ``reject`` (short-circuits — cost governor);
  * the first stage that raises → ``validation_pending`` (unverifiable; short-circuits);
  * otherwise, if any stage flagged ``validation_pending`` → ``validation_pending``;
  * otherwise, if any stage flagged ``needs_human_review`` → ``needs_human_review``;
  * otherwise (all passed) → ``trigger_ready_research_candidate``.

Only ``reject`` and an exception short-circuit. A ``validation_pending`` or
``needs_human_review`` disposition does NOT — later stages still run, so a
subsequent hard reject always wins (correct rejection is the point). An
unrecognized disposition is fail-closed to ``reject`` (hardened, never softened).
Every label is a canonical research label (docs/label_policy.md) — never an
action word.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from project_money.validation.invariants import (
    CheckResult,
    FAILURE_DISPOSITIONS,
    NEEDS_HUMAN_REVIEW,
    REJECT,
    VALIDATION_PENDING,
)

StageFn = Callable[[Any], tuple]

# Severity of a failing stage's disposition (higher = more blocking). Used both
# for the terminal-label precedence and for naming the deciding stage. An unknown
# disposition is treated as the hardest (reject) — fail closed.
_SEVERITY = {REJECT: 3, VALIDATION_PENDING: 2, NEEDS_HUMAN_REVIEW: 1}


@dataclass(frozen=True)
class Stage:
    """One cascade stage. ``fn(candidate)`` -> ``(passed, metrics, reasons)`` or
    ``(passed, metrics, reasons, disposition)``."""

    name: str
    fn: StageFn

    @classmethod
    def from_check(cls, name: str, check: Callable[[Any], CheckResult]) -> "Stage":
        """Wrap a ``CheckResult``-returning check as a cascade stage, propagating its
        ``disposition`` so a soft failure yields the matching label (not a hard
        ``reject``). ``check`` receives the candidate; close over it to adapt a
        check whose signature differs (e.g. one taking ``y_true, y_pred``).
        Registering a check here does not change its own logic — only how the
        cascade labels a failure."""

        def fn(candidate: Any) -> tuple:
            r = check(candidate)
            return r.passed, {}, list(r.reasons), r.disposition

        return cls(name, fn)


@dataclass
class StageResult:
    name: str
    passed: bool
    metrics: dict[str, float] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    disposition: str = REJECT


@dataclass
class CascadeResult:
    """Full record of one candidate's run through the cascade.

    ``label`` is one of the canonical research labels (docs/label_policy.md):
    ``trigger_ready_research_candidate`` only when every stage passed;
    ``needs_human_review`` / ``validation_pending`` when the worst failure was a
    review flag / an unverifiable check; ``reject`` when a stage hard-rejected.
    Never an action word. See the module header for the full precedence.
    """

    stages: list[StageResult] = field(default_factory=list)
    label: str = "validation_pending"

    @property
    def passed(self) -> bool:
        return self.label == "trigger_ready_research_candidate"

    @property
    def failed_stage(self) -> str | None:
        """The stage that determined a non-promote outcome: the most-severe failing
        stage (reject > validation_pending > needs_human_review), first occurrence.
        Because a soft failure does not short-circuit, under e.g. review-then-reject
        this names the reject cause — not the earlier review — so the ledger records
        *why* a candidate did not promote."""
        non_passing = [s for s in self.stages if not s.passed]
        if not non_passing:
            return None
        worst = max(_SEVERITY.get(s.disposition, 3) for s in non_passing)
        return next(s.name for s in non_passing if _SEVERITY.get(s.disposition, 3) == worst)

    def _stages_flagged(self, disposition: str) -> list[str]:
        return [s.name for s in self.stages if not s.passed and s.disposition == disposition]

    @property
    def review_stages(self) -> list[str]:
        """Non-passing stages that flagged for human review."""
        return self._stages_flagged(NEEDS_HUMAN_REVIEW)

    @property
    def unverifiable_stages(self) -> list[str]:
        """Non-passing stages that could not certify (validation_pending)."""
        return self._stages_flagged(VALIDATION_PENDING)

    def merged_metrics(self) -> dict[str, float]:
        """Stage-prefixed union of every stage's metrics dict."""
        out: dict[str, float] = {}
        for s in self.stages:
            for k, v in s.metrics.items():
                out[f"{s.name}.{k}"] = v
        return out


def _normalize_output(out: Any) -> tuple[bool, dict[str, float], list[str], str]:
    """Coerce a stage's return into ``(passed, metrics, reasons, disposition)``.

    Accepts a 3- or 4-tuple; a 3-tuple defaults the disposition to ``reject``. An
    unrecognized disposition is fail-closed to ``reject`` with a diagnostic reason
    (hardened, never softened). Raises ``TypeError`` on a malformed shape so
    ``run_cascade`` records it as ``validation_pending`` (unverifiable).
    """
    if not isinstance(out, tuple) or len(out) not in (3, 4):
        raise TypeError(
            "stage must return (passed, metrics, reasons[, disposition]); "
            f"got {type(out).__name__} {out!r}"
        )
    if len(out) == 3:
        passed, metrics, reasons = out
        disposition = REJECT
    else:
        passed, metrics, reasons, disposition = out
    passed = bool(passed)
    reasons = list(reasons)
    if disposition not in FAILURE_DISPOSITIONS:
        if not passed:  # a passing stage's disposition is never consulted — don't pollute its reasons
            reasons.append(f"unrecognized disposition {disposition!r} — treated as reject (fail closed)")
        disposition = REJECT
    return passed, dict(metrics), reasons, disposition


def run_cascade(candidate: Any, stages: list[Stage]) -> CascadeResult:
    """Run ``candidate`` through ``stages`` in order with the disposition-aware
    precedence documented in the module header.

    A hard ``reject`` (or an exception → ``validation_pending``) short-circuits; a
    ``validation_pending`` / ``needs_human_review`` disposition is recorded but does
    not, so a later hard reject can still win. Exceptions inside a stage are
    captured as that stage's failure reasons (unverifiable ≠ rejected — the
    distinction feeds the verification-debt ledger).
    """
    result = CascadeResult()
    stages = list(stages)  # materialize any iterable so the empty-guard is total, not list-only
    if not stages:
        result.label = "validation_pending"  # nothing was verified — not promotable, not rejected
        return result
    review_pending = False
    unverifiable = False
    for stage in stages:
        try:
            passed, metrics, reasons, disposition = _normalize_output(stage.fn(candidate))
        except Exception as exc:  # captured, never swallowed
            result.stages.append(
                StageResult(
                    stage.name, False, {}, [f"stage raised {type(exc).__name__}: {exc}"], VALIDATION_PENDING
                )
            )
            result.label = "validation_pending"
            return result
        result.stages.append(StageResult(stage.name, passed, metrics, reasons, disposition))
        if not passed:
            if disposition == REJECT:
                result.label = "reject"
                return result
            if disposition == VALIDATION_PENDING:
                unverifiable = True  # do NOT short-circuit: a later reject must be able to outrank
            else:  # NEEDS_HUMAN_REVIEW
                review_pending = True
    if unverifiable:
        result.label = "validation_pending"
    elif review_pending:
        result.label = "needs_human_review"
    else:
        result.label = "trigger_ready_research_candidate"
    return result
