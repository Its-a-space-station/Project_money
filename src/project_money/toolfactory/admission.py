"""Independent admission gate for generated/authored tools — the gate
TOOLMAKER demonstrably lacks (a tool that self-assessed "successful" on its
one creation example was silently wrong on held-out inputs).

Maker ≠ checker at the tool level (synthesis §4 tool 9):

- held-out invocations must **differ from the creation example** — compared
  after binding to the function signature with defaults applied, so omitting
  a defaulted parameter cannot disguise the same call (SWE-smith checker-leak
  guard);
- every held-out case must constrain something (expected value, predicate, or
  battery-level property checks) — an unconstrained case is a vacuous pass;
- known-answer tests compare against independently computed references, with
  type-aware semantics (bool never matches int; int/float compare under
  tolerance; numpy/pandas compared structurally, never crashing the gate);
- a determinism check runs every case twice and requires identical output
  (GLM-5: determinism is a gate, not a nicety);
- time-series/signal tools MUST additionally supply ``lookahead_check`` wiring
  ``project_money.validation.check_no_lookahead`` (or equivalent); its failure
  fails admission;
- only a passing report may register the tool (``register_validated``).

Scope note: the synthesis' TOOLMAKER-style *build* side (checkpointed sandbox
build with diagnose→reimplement→summarise memory) is deliberately deferred —
this module is the admission gate only; the build harness is tracked in
tasks/todo.md and gated like all new capability.

Research-only: the gate validates *read-only research tools*; the registry it
feeds refuses anything else by construction.
"""

from __future__ import annotations

import inspect
import json
import math
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class AdmissionCase:
    """One held-out validation case.

    ``expected`` (optional) is a known-answer reference computed independently
    of the tool under test. ``predicate`` (optional) receives the output and
    returns an error string or None. A case with neither — when the battery
    also has no property checks — fails validation as unconstrained.
    """

    inputs: dict[str, Any]
    expected: Any | None = None
    predicate: Callable[[Any], str | None] | None = None
    rel_tol: float = 1e-9


@dataclass
class AdmissionReport:
    passed: bool
    reasons: list[str] = field(default_factory=list)
    n_cases: int = 0
    determinism_ok: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "reasons": list(self.reasons),
            "n_cases": self.n_cases,
            "determinism_ok": self.determinism_ok,
        }


def _canon_value(v: Any) -> str:
    return json.dumps(v, sort_keys=True, default=str)


def _normalized_call(fn: Callable[..., Any], inputs: dict[str, Any]) -> str:
    """Canonical form of an invocation: bind to the signature, apply defaults,
    serialize. Two invocations that execute identically normalize identically
    even if one omits defaulted parameters."""
    try:
        bound = inspect.signature(fn).bind(**inputs)
        bound.apply_defaults()
        args = dict(bound.arguments)
    except (TypeError, ValueError):
        args = dict(inputs)
    return _canon_value(args)


def _values_match(a: Any, b: Any, rel_tol: float) -> bool:
    """Type-aware equality that can never raise.

    bool matches only bool; int/float (non-bool) compare under tolerance;
    dicts/sequences recurse; pandas objects use .equals; numpy arrays use
    allclose. Any comparison exception counts as a mismatch, never a crash —
    a gate that crashes fails open somewhere else.
    """
    try:
        if isinstance(a, bool) or isinstance(b, bool):
            return isinstance(a, bool) and isinstance(b, bool) and a == b
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            fa, fb = float(a), float(b)
            if math.isnan(fa) and math.isnan(fb):
                return True
            return math.isclose(fa, fb, rel_tol=rel_tol, abs_tol=rel_tol)
        if isinstance(a, dict) and isinstance(b, dict):
            return a.keys() == b.keys() and all(
                _values_match(a[k], b[k], rel_tol) for k in a
            )
        if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            return len(a) == len(b) and all(
                _values_match(x, y, rel_tol) for x, y in zip(a, b)
            )
        if isinstance(a, (pd.DataFrame, pd.Series)):
            return type(a) is type(b) and a.equals(b)
        if isinstance(a, np.ndarray):
            return (
                isinstance(b, np.ndarray)
                and a.shape == b.shape
                and bool(np.allclose(a, b, rtol=rel_tol, atol=rel_tol, equal_nan=True))
            )
        return bool(a == b)
    except Exception:
        return False


def validate_tool(
    fn: Callable[..., Any],
    creation_example: dict[str, Any],
    held_out_cases: list[AdmissionCase],
    *,
    property_checks: tuple[Callable[[Any], str | None], ...] = (),
    determinism_runs: int = 2,
    lookahead_check: Callable[[], Any] | None = None,
) -> AdmissionReport:
    """Run the full admission battery against ``fn``.

    ``lookahead_check`` is MANDATORY for any tool that produces time-indexed
    signals/weights: wire ``project_money.validation.check_no_lookahead`` (or
    an equivalent returning an object with ``.passed``/``.reasons``); its
    failure fails admission. Non-temporal tools may omit it.

    Failure conditions (all collected, none silently dropped):
    - no held-out case, or every case normalizing to the creation invocation;
    - a case constraining nothing (no expected, no predicate, no battery-level
      property checks);
    - any case raising;
    - non-deterministic output across ``determinism_runs`` identical calls;
    - known-answer mismatch or predicate/property failure;
    - a failing lookahead check.
    """
    report = AdmissionReport(passed=False, n_cases=len(held_out_cases))

    if not held_out_cases:
        report.reasons.append(
            "no held-out cases supplied — creation-example-only validation is unsafe"
        )
        return report

    creation_norm = _normalized_call(fn, creation_example)
    if all(_normalized_call(fn, c.inputs) == creation_norm for c in held_out_cases):
        report.reasons.append(
            "all held-out cases normalize to the creation invocation "
            "(defaults applied) — nothing was held out"
        )
        return report

    if lookahead_check is not None:
        try:
            la = lookahead_check()
            la_passed = bool(getattr(la, "passed", la))
            if not la_passed:
                la_reasons = getattr(la, "reasons", None) or ["(no detail)"]
                report.reasons.append(f"lookahead check failed: {la_reasons}")
        except Exception as exc:
            report.reasons.append(
                f"lookahead check raised {type(exc).__name__}: {exc}"
            )

    determinism_ok = True
    for i, case in enumerate(held_out_cases):
        if case.expected is None and case.predicate is None and not property_checks:
            report.reasons.append(
                f"case {i}: constrains nothing (no expected value, no predicate, "
                "and no battery-level property checks) — vacuous case"
            )
            continue

        outputs = []
        for _ in range(max(2, determinism_runs)):
            try:
                outputs.append(fn(**case.inputs))
            except Exception as exc:
                report.reasons.append(f"case {i}: raised {type(exc).__name__}: {exc}")
                outputs = []
                break
        if not outputs:
            continue

        first = outputs[0]
        for run_idx, out in enumerate(outputs[1:], start=2):
            if not _values_match(first, out, rel_tol=1e-12):
                determinism_ok = False
                report.reasons.append(
                    f"case {i}: non-deterministic output (run 1 vs run {run_idx})"
                )
                break

        if case.expected is not None and not _values_match(
            first, case.expected, case.rel_tol
        ):
            report.reasons.append(
                f"case {i}: known-answer mismatch (got {first!r}, expected {case.expected!r})"
            )
        if case.predicate is not None:
            try:
                err = case.predicate(first)
            except Exception as exc:
                err = f"predicate raised {type(exc).__name__}: {exc}"
            if err:
                report.reasons.append(f"case {i}: predicate failed: {err}")
        for j, check in enumerate(property_checks):
            try:
                err = check(first)
            except Exception as exc:
                err = f"property check raised {type(exc).__name__}: {exc}"
            if err:
                report.reasons.append(f"case {i}: property check {j} failed: {err}")

    report.determinism_ok = determinism_ok
    report.passed = not report.reasons
    return report


def register_validated(registry, spec, fn, report: AdmissionReport) -> None:
    """Register ``spec`` only if ``report.passed`` — the wiring that makes the
    gate mandatory rather than advisory. Raises on a failing report."""
    if not report.passed:
        raise ValueError(
            "admission report did not pass; refusing to register "
            f"{spec.name!r}: {report.reasons}"
        )
    registry.register(spec, admission_report=report.as_dict())
