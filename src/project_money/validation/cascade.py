"""Staged evaluation cascade with an explicit, published promotion policy.

The cost governor and junk filter (DGM's 10→60→200 gates; AlphaEvolve's
hypothesis-testing cascade; synthesis §4 tool 1): cheap deterministic screens
run first, expensive evaluation is reserved for survivors, every stage's
verdict and evidence are recorded, and a failure is never silently dropped —
the cascade result names the failing stage and its reasons (verification-debt
doctrine).

Stages are plain callables returning a (passed, metrics, reasons) triple, so
the cascade is generic over what is being evaluated. Thresholds live in the
stage definitions — config, not vibes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

StageFn = Callable[[Any], tuple[bool, dict[str, float], list[str]]]


@dataclass(frozen=True)
class Stage:
    """One cascade stage. ``fn(candidate)`` -> (passed, metrics, reasons)."""

    name: str
    fn: StageFn


@dataclass
class StageResult:
    name: str
    passed: bool
    metrics: dict[str, float] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)


@dataclass
class CascadeResult:
    """Full record of one candidate's run through the cascade.

    ``label`` is one of the canonical research labels (see
    docs/label_policy.md): ``trigger_ready_research_candidate`` only when every
    stage passed; ``reject`` when a stage failed; ``validation_pending`` when
    the cascade was cut short by an error. Never an action word.
    """

    stages: list[StageResult] = field(default_factory=list)
    label: str = "validation_pending"

    @property
    def passed(self) -> bool:
        return self.label == "trigger_ready_research_candidate"

    @property
    def failed_stage(self) -> str | None:
        for s in self.stages:
            if not s.passed:
                return s.name
        return None

    def merged_metrics(self) -> dict[str, float]:
        """Stage-prefixed union of every stage's metrics dict."""
        out: dict[str, float] = {}
        for s in self.stages:
            for k, v in s.metrics.items():
                out[f"{s.name}.{k}"] = v
        return out


def run_cascade(candidate: Any, stages: list[Stage]) -> CascadeResult:
    """Run ``candidate`` through ``stages`` in order, stopping at first failure.

    Exceptions inside a stage are captured as that stage's failure reasons and
    the result is labeled ``validation_pending`` (unverifiable ≠ rejected —
    the distinction feeds the verification-debt ledger).
    """
    result = CascadeResult()
    for stage in stages:
        try:
            passed, metrics, reasons = stage.fn(candidate)
        except Exception as exc:  # captured, never swallowed
            result.stages.append(
                StageResult(stage.name, False, {}, [f"stage raised {type(exc).__name__}: {exc}"])
            )
            result.label = "validation_pending"
            return result
        result.stages.append(StageResult(stage.name, passed, metrics, reasons))
        if not passed:
            result.label = "reject"
            return result
    result.label = "trigger_ready_research_candidate"
    return result
