"""Staged evaluation cascade with an explicit, published promotion policy.

The cost governor and junk filter (DGM's 10→60→200 gates; AlphaEvolve's
hypothesis-testing cascade; synthesis §4 tool 1): cheap deterministic screens
run first, expensive evaluation is reserved for survivors, every stage's
verdict and evidence are recorded, and a failure is never silently dropped —
the cascade result names the failing stage and its reasons (verification-debt
doctrine).

Stages are plain callables returning a ``(passed, metrics, reasons)`` triple, or
a ``(passed, metrics, reasons, disposition)`` quadruple when a failure is a
*review* flag rather than a hard reject, so the cascade is generic over what is
being evaluated. Thresholds live in the stage definitions — config, not vibes.

Failure disposition & label precedence. A failing stage's disposition is either
``reject`` (hard disqualification, the default) or ``needs_human_review`` (route
to a human, not an auto-reject — e.g. an implausibly high directional accuracy or
a strong-but-plausible returns edge). So a review flag can never *mask* a harder
verdict, the terminal label is decided as:

  * the first stage that hard-``reject``s → ``reject`` (short-circuits — cost governor);
  * the first stage that raises → ``validation_pending`` (unverifiable ≠ rejected;
    short-circuits);
  * otherwise, if any stage flagged ``needs_human_review`` → ``needs_human_review``;
  * otherwise (all passed) → ``trigger_ready_research_candidate``.

A ``needs_human_review`` deliberately does **not** short-circuit: later stages
still run, so a subsequent hard reject or an unverifiable stage still wins (a
review flag must never let a rejectable candidate slip past — correct rejection
is the point). An unrecognized disposition from a stage is fail-closed to
``reject`` (hardened, never softened) with a diagnostic reason. Every label is a
canonical research label (docs/label_policy.md) — never an action word.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from project_money.validation.invariants import (
    CheckResult,
    FAILURE_DISPOSITIONS,
    NEEDS_HUMAN_REVIEW,
    REJECT,
)

StageFn = Callable[[Any], tuple]


@dataclass(frozen=True)
class Stage:
    """One cascade stage. ``fn(candidate)`` -> ``(passed, metrics, reasons)`` or
    ``(passed, metrics, reasons, disposition)``."""

    name: str
    fn: StageFn

    @classmethod
    def from_check(cls, name: str, check: Callable[[Any], CheckResult]) -> "Stage":
        """Wrap a ``CheckResult``-returning check as a cascade stage, propagating its
        ``disposition`` so a review-flagged failure yields ``needs_human_review``
        rather than a hard ``reject``. ``check`` receives the candidate; close over
        it to adapt a check whose signature differs (e.g. one taking ``y_true,
        y_pred``). Registering a check here does not change its own logic — only
        how the cascade labels a failure."""

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
    ``needs_human_review`` when the worst failure was a review flag; ``reject``
    when a stage hard-rejected; ``validation_pending`` when the cascade was cut
    short by an error. Never an action word. See the module header for the full
    precedence.
    """

    stages: list[StageResult] = field(default_factory=list)
    label: str = "validation_pending"

    @property
    def passed(self) -> bool:
        return self.label == "trigger_ready_research_candidate"

    @property
    def failed_stage(self) -> str | None:
        """The stage that determined a non-promote outcome: the hard-reject /
        unverifiable stage when one exists, else the first review flag. Because a
        review flag does not short-circuit, under review-then-reject this names the
        reject cause — not the earlier review — so the ledger records *why* a
        candidate was rejected."""
        non_passing = [s for s in self.stages if not s.passed]
        if not non_passing:
            return None
        for s in non_passing:
            if s.disposition == REJECT:
                return s.name
        return non_passing[0].name

    @property
    def review_stages(self) -> list[str]:
        """Names of the non-passing stages that flagged for human review (empty on
        a hard reject or an all-pass run)."""
        return [s.name for s in self.stages if not s.passed and s.disposition == NEEDS_HUMAN_REVIEW]

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
    ``needs_human_review`` is recorded but does not, so a later hard reject can
    still win. Exceptions inside a stage are captured as that stage's failure
    reasons (unverifiable ≠ rejected — the distinction feeds the verification-debt
    ledger).
    """
    result = CascadeResult()
    stages = list(stages)  # materialize any iterable so the empty-guard is total, not list-only
    if not stages:
        result.label = "validation_pending"  # nothing was verified — not promotable, not rejected
        return result
    review_pending = False
    for stage in stages:
        try:
            passed, metrics, reasons, disposition = _normalize_output(stage.fn(candidate))
        except Exception as exc:  # captured, never swallowed
            result.stages.append(
                StageResult(stage.name, False, {}, [f"stage raised {type(exc).__name__}: {exc}"], REJECT)
            )
            result.label = "validation_pending"
            return result
        result.stages.append(StageResult(stage.name, passed, metrics, reasons, disposition))
        if not passed:
            if disposition == NEEDS_HUMAN_REVIEW:
                review_pending = True  # do NOT short-circuit: a later reject must be able to outrank
                continue
            result.label = "reject"
            return result
    result.label = "needs_human_review" if review_pending else "trigger_ready_research_candidate"
    return result
