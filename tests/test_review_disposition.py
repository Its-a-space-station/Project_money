"""DEBT-review-disposition — machine-readable needs_human_review vs reject.

Covers the three layers of the fix:
  1. ``CheckResult.disposition`` — the field + its validation.
  2. ``run_cascade`` precedence — a review flag never short-circuits, so a later
     hard reject / exception still wins; only an all-pass run promotes.
  3. The review-flavored checks (S11 / S5 / S10 / S26) emit the correct
     disposition, and ``Stage.from_check`` carries it end-to-end.

The safety property under test: a ``needs_human_review`` can never *mask* a
``reject`` or an unverifiable stage (correct rejection is the point).
"""

import numpy as np
import pytest

from project_money.validation import (
    CheckResult,
    NEEDS_HUMAN_REVIEW,
    REJECT,
    Stage,
    check_calibration,
    check_cost_gate,
    check_directional_accuracy_plausible,
    check_horizon_monotonicity,
    check_returns_not_levels,
    run_cascade,
)
from tests.specimens import (
    contemporaneous_returns_leak,
    overconfident_forecast,
    returns_contemporaneous_leak_moderate,
)


# --- stage helpers that record execution order --------------------------------
def _stage(name, passed, disposition=REJECT, *, calls=None):
    def fn(c):
        if calls is not None:
            calls.append(name)
        reasons = [] if passed else [f"{name} failed"]
        return (passed, {"s": 1.0 if passed else 0.0}, reasons, disposition)

    return Stage(name, fn)


def _legacy_stage(name, passed, *, calls=None):
    """A pre-disposition 3-tuple stage (backward-compat path)."""

    def fn(c):
        if calls is not None:
            calls.append(name)
        return (passed, {}, [] if passed else ["nope"])

    return Stage(name, fn)


def _raising_stage(name, *, calls=None):
    def fn(c):
        if calls is not None:
            calls.append(name)
        raise RuntimeError("boom")

    return Stage(name, fn)


class TestCheckResultDisposition:
    def test_default_is_reject(self):
        assert CheckResult("x", False, ["r"]).disposition == REJECT

    def test_accepts_needs_human_review(self):
        assert CheckResult("x", False, ["r"], NEEDS_HUMAN_REVIEW).disposition == NEEDS_HUMAN_REVIEW

    def test_rejects_unknown_disposition(self):
        with pytest.raises(ValueError):
            CheckResult("x", False, ["r"], "needs_review")  # typo, not canonical

    def test_action_word_disposition_rejected(self):
        with pytest.raises(ValueError):
            CheckResult("x", False, ["r"], "buy")

    def test_is_frozen_disposition_cannot_be_softened(self):
        # Skeptic #3: a validated disposition must not be softened by post-hoc assignment.
        r = CheckResult("x", False, ["r"], REJECT)
        with pytest.raises(Exception):  # FrozenInstanceError
            r.disposition = NEEDS_HUMAN_REVIEW


class TestCascadePrecedence:
    def test_review_only_yields_needs_human_review(self):
        result = run_cascade("c", [_stage("r", False, NEEDS_HUMAN_REVIEW)])
        assert result.label == "needs_human_review"
        assert not result.passed
        assert result.review_stages == ["r"]
        assert result.failed_stage == "r"

    def test_reject_outranks_earlier_review_and_both_run(self):
        # review does NOT short-circuit, so the later hard reject still fires and wins.
        calls = []
        result = run_cascade(
            "c",
            [_stage("review", False, NEEDS_HUMAN_REVIEW, calls=calls), _stage("hard", False, REJECT, calls=calls)],
        )
        assert result.label == "reject"
        assert calls == ["review", "hard"]  # review did not short-circuit
        assert result.review_stages == ["review"]  # still recorded

    def test_reject_short_circuits_and_masks_later_review(self):
        calls = []
        result = run_cascade(
            "c",
            [_stage("hard", False, REJECT, calls=calls), _stage("review", False, NEEDS_HUMAN_REVIEW, calls=calls)],
        )
        assert result.label == "reject"
        assert calls == ["hard"]  # reject short-circuited; review never ran

    def test_review_then_pass_is_needs_human_review(self):
        calls = []
        result = run_cascade(
            "c", [_stage("review", False, NEEDS_HUMAN_REVIEW, calls=calls), _stage("ok", True, calls=calls)]
        )
        assert result.label == "needs_human_review"
        assert calls == ["review", "ok"]

    def test_review_then_exception_is_validation_pending(self):
        # An unverifiable stage still wins over a pending review flag.
        result = run_cascade("c", [_stage("review", False, NEEDS_HUMAN_REVIEW), _raising_stage("boom")])
        assert result.label == "validation_pending"

    def test_all_pass_with_review_disposition_on_pass_is_ignored(self):
        # disposition is meaningless when passed=True.
        result = run_cascade("c", [_stage("a", True, NEEDS_HUMAN_REVIEW), _stage("b", True)])
        assert result.label == "trigger_ready_research_candidate"
        assert result.review_stages == []

    def test_unknown_disposition_fails_closed_to_reject(self):
        bogus = Stage("bogus", lambda c: (False, {}, ["x"], "needs_review"))  # typo
        result = run_cascade("c", [bogus])
        assert result.label == "reject"
        assert any("treated as reject" in r for r in result.stages[-1].reasons)

    def test_malformed_output_is_validation_pending(self):
        bad = Stage("bad", lambda c: "not a tuple")
        result = run_cascade("c", [bad])
        assert result.label == "validation_pending"

    def test_legacy_three_tuple_failure_still_rejects(self):
        result = run_cascade("c", [_legacy_stage("legacy", False)])
        assert result.label == "reject"
        assert result.stages[-1].disposition == REJECT

    # --- red-team regressions (skeptic round 1) ---

    def test_failed_stage_names_rejecter_not_earlier_review(self):
        # Skeptic #1: review does not short-circuit, so failed_stage must still point
        # at the reject cause (the ledger records *why* it was rejected), not the review.
        result = run_cascade(
            "c", [_stage("review", False, NEEDS_HUMAN_REVIEW), _stage("hard", False, REJECT)]
        )
        assert result.label == "reject"
        assert result.failed_stage == "hard"

    def test_failed_stage_names_review_when_no_reject(self):
        result = run_cascade("c", [_stage("ok", True), _stage("review", False, NEEDS_HUMAN_REVIEW)])
        assert result.label == "needs_human_review"
        assert result.failed_stage == "review"

    def test_empty_cascade_is_validation_pending_not_promoted(self):
        # Skeptic #2: a no-op cascade must NOT promote (fail-closed).
        result = run_cascade("c", [])
        assert result.label == "validation_pending"
        assert not result.passed
        assert result.failed_stage is None

    def test_empty_generator_is_validation_pending_not_promoted(self):
        # Skeptic re-verify: the empty-guard must be total (any empty iterable), not list-only.
        result = run_cascade("c", (s for s in []))
        assert result.label == "validation_pending"
        assert not result.passed

    def test_passing_stage_with_garbage_disposition_has_clean_reasons(self):
        # Skeptic #4: a passing stage's disposition is never consulted — don't pollute its reasons.
        result = run_cascade("c", [Stage("ok", lambda c: (True, {}, [], "buy"))])
        assert result.label == "trigger_ready_research_candidate"
        assert result.stages[-1].reasons == []


class TestFromCheckEndToEnd:
    def test_review_check_yields_needs_human_review(self):
        stage = Stage.from_check("s11", lambda c: check_directional_accuracy_plausible(0.9))
        assert run_cascade("cand", [stage]).label == "needs_human_review"

    def test_passing_check_promotes(self):
        stage = Stage.from_check("s11", lambda c: check_directional_accuracy_plausible(0.5))
        assert run_cascade("cand", [stage]).label == "trigger_ready_research_candidate"

    def test_reject_check_rejects(self):
        stage = Stage.from_check("s16", lambda c: check_cost_gate(cost_bps=None))
        assert run_cascade("cand", [stage]).label == "reject"

    def test_review_check_then_reject_check_rejects(self):
        review = Stage.from_check("s11", lambda c: check_directional_accuracy_plausible(0.9))
        reject = Stage.from_check("s16", lambda c: check_cost_gate(cost_bps=None))
        assert run_cascade("cand", [review, reject]).label == "reject"


class TestS11Disposition:
    def test_implausible_accuracy_is_review(self):
        r = check_directional_accuracy_plausible(0.9)
        assert not r.passed and r.disposition == NEEDS_HUMAN_REVIEW

    def test_plausible_accuracy_passes(self):
        assert check_directional_accuracy_plausible(0.5).passed

    def test_bad_input_fails_closed_to_reject(self):
        for bad in ("not-a-number", 1.5, float("nan")):
            r = check_directional_accuracy_plausible(bad)
            assert not r.passed and r.disposition == REJECT


class TestS16Disposition:
    def test_costs_not_modeled_is_reject(self):
        r = check_cost_gate(cost_bps=None)
        assert not r.passed and r.disposition == REJECT


class TestS5Disposition:
    def test_moderate_returns_leak_is_review(self):
        y_true, y_pred = returns_contemporaneous_leak_moderate()
        r = check_returns_not_levels(y_true, y_pred)
        assert not r.passed and r.disposition == NEEDS_HUMAN_REVIEW

    def test_r2_near_one_leak_is_reject(self):
        # R²≈1 trips the unconditional hard reason — reject outranks any review.
        y_true, y_pred = contemporaneous_returns_leak()
        r = check_returns_not_levels(y_true, y_pred, is_levels=False)
        assert not r.passed and r.disposition == REJECT

    def test_insufficient_sample_fails_closed_to_reject(self):
        r = check_returns_not_levels([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert not r.passed and r.disposition == REJECT


class TestS10Disposition:
    def test_inverted_curve_is_reject(self):
        # Split (skeptic #5): a strictly decreasing curve is a hard leakage fingerprint.
        r = check_horizon_monotonicity({1: 2.0, 5: 1.5, 10: 1.0})
        assert not r.passed and r.disposition == REJECT

    def test_flat_uneven_curve_is_review(self):
        # A flat / endpoint-only-jump curve (not inverted) stays needs_human_review.
        r = check_horizon_monotonicity({1: 0.010, 5: 0.010, 10: 0.010, 20: 0.010, 30: 0.0106})
        assert not r.passed and r.disposition == NEEDS_HUMAN_REVIEW

    def test_single_horizon_fails_closed_to_reject(self):
        r = check_horizon_monotonicity({1: 0.5})
        assert not r.passed and r.disposition == REJECT


class TestS26Disposition:
    def test_overconfident_is_review(self):
        p, y = overconfident_forecast()
        r = check_calibration(p, y)
        assert not r.passed and r.disposition == NEEDS_HUMAN_REVIEW

    def test_out_of_range_fails_closed_to_reject(self):
        p = np.full(200, 1.5)
        y = (np.arange(200) % 2).astype(float)
        r = check_calibration(p, y)
        assert not r.passed and r.disposition == REJECT
