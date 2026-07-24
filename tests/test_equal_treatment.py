"""V2 — equal-treatment protocol for a candidate-vs-null comparison.

A candidate only "beats the null" if both arms shared the same split, the same
preprocessing, and an equal hyperparameter budget. Every failure is
``validation_pending`` (the comparison is unverifiable, the strategy is not
disqualified). The load-bearing property is the anti-vacuous-pass guard: an
un-instrumented comparison must FAIL, never silently pass.
"""

import numpy as np
import pandas as pd
import pytest

from project_money.validation import (
    Stage,
    TreatmentRecord,
    VALIDATION_PENDING,
    check_equal_treatment,
    run_cascade,
    treatment_fingerprint,
)


def _fair(**overrides):
    base = dict(split_id="s", preprocessing_id="p", hp_budget=10)
    base.update(overrides)
    return TreatmentRecord(**base)


class TestTreatmentFingerprint:
    def test_deterministic(self):
        idx = pd.date_range("2020-01-01", periods=50)
        assert treatment_fingerprint(idx) == treatment_fingerprint(idx)

    def test_order_invariant(self):
        # A split is defined by its member set; row order must not change the id.
        assert treatment_fingerprint([3, 1, 2]) == treatment_fingerprint([1, 2, 3])
        assert treatment_fingerprint({"a": 1, "b": 2}) == treatment_fingerprint({"b": 2, "a": 1})

    def test_different_content_differs(self):
        assert treatment_fingerprint([1, 2, 3]) != treatment_fingerprint([1, 2, 4])

    def test_numpy_and_pandas_match_list(self):
        assert treatment_fingerprint(np.array([1, 2, 3])) == treatment_fingerprint([1, 2, 3])

    def test_none_raises_not_hashes_to_constant(self):
        with pytest.raises(ValueError):
            treatment_fingerprint(None)

    def test_empty_collection_raises_not_hashes_to_constant(self):
        # Round-4 caveat 2: an empty split/descriptor must fail closed, not hash to sha256("").
        for empty in ([], {}, set(), tuple()):
            with pytest.raises(ValueError):
                treatment_fingerprint(empty)


class TestCheckEqualTreatment:
    def test_fair_comparison_passes(self):
        assert check_equal_treatment(_fair(), _fair()).passed

    def test_all_failures_are_validation_pending(self):
        r = check_equal_treatment(_fair(hp_budget=1), _fair(hp_budget=100))
        assert not r.passed and r.disposition == VALIDATION_PENDING

    def test_asymmetric_budget_flagged(self):
        r = check_equal_treatment(_fair(hp_budget=1), _fair(hp_budget=100))
        assert not r.passed and any("asymmetric" in x for x in r.reasons)

    def test_budget_tolerance_respected(self):
        assert check_equal_treatment(_fair(hp_budget=10), _fair(hp_budget=11), budget_tol=1).passed
        assert not check_equal_treatment(_fair(hp_budget=10), _fair(hp_budget=12), budget_tol=1).passed

    def test_differing_split_flagged(self):
        r = check_equal_treatment(_fair(split_id="a"), _fair(split_id="b"))
        assert not r.passed and any("splits differ" in x for x in r.reasons)

    def test_differing_preprocessing_flagged(self):
        r = check_equal_treatment(_fair(preprocessing_id="a"), _fair(preprocessing_id="b"))
        assert not r.passed and any("preprocessing differs" in x for x in r.reasons)

    def test_negative_budget_fails_closed(self):
        assert not check_equal_treatment(_fair(hp_budget=-1), _fair(hp_budget=-1)).passed

    # --- anti-vacuous-pass: un-instrumented comparison must FAIL, never pass ---

    def test_empty_record_fails_closed(self):
        r = check_equal_treatment(TreatmentRecord(), TreatmentRecord())
        assert not r.passed and r.disposition == VALIDATION_PENDING

    def test_missing_any_field_fails_closed(self):
        assert not check_equal_treatment(_fair(split_id=None), _fair()).passed
        assert not check_equal_treatment(_fair(preprocessing_id=None), _fair()).passed
        assert not check_equal_treatment(_fair(), _fair(hp_budget=None)).passed

    def test_fingerprint_derived_ids_pass_when_equal(self):
        idx = pd.date_range("2020-01-01", periods=100)
        sid = treatment_fingerprint(idx)
        pid = treatment_fingerprint({"scaler": "none", "window": 20})
        rec = TreatmentRecord(split_id=sid, preprocessing_id=pid, hp_budget=5)
        assert check_equal_treatment(rec, rec).passed

    # --- red-team round-3 regressions (skeptic + code review) ---

    def test_nan_budget_fails_closed(self):
        # A non-finite budget is un-instrumented, not zero — must not slip through <,>,abs.
        nan = float("nan")
        assert not check_equal_treatment(_fair(hp_budget=nan), _fair()).passed
        assert not check_equal_treatment(_fair(hp_budget=nan), _fair(hp_budget=nan)).passed

    def test_inf_budget_fails_closed(self):
        assert not check_equal_treatment(_fair(hp_budget=float("inf")), _fair(hp_budget=float("inf"))).passed

    def test_non_integer_budget_fails_closed(self):
        assert not check_equal_treatment(_fair(hp_budget=10.5), _fair(hp_budget=10.5)).passed

    def test_nan_tolerance_cannot_disable_asymmetry_check(self):
        r = check_equal_treatment(_fair(hp_budget=1), _fair(hp_budget=1000), budget_tol=float("nan"))
        assert not r.passed and r.disposition == VALIDATION_PENDING

    def test_numeric_string_budget_fails_closed_without_raising(self):
        # Round-4 caveat 1: a non-numeric budget returns a clean reason, not a downstream TypeError.
        r = check_equal_treatment(_fair(hp_budget="10"), _fair(hp_budget="10"))
        assert not r.passed and r.disposition == VALIDATION_PENDING


class TestFingerprintCollisionSafety:
    def test_type_aware_int_vs_str(self):
        # 1 (int) and "1" (str) are different content and must not collide.
        assert treatment_fingerprint([1, 2, 3]) != treatment_fingerprint(["1", "2", "3"])

    def test_delimiter_cannot_forge_a_collision(self):
        # An in-value pipe must not make two different member sets hash equal.
        assert treatment_fingerprint(["1|2", "3"]) != treatment_fingerprint(["1", "2", "3"])

    def test_dict_delimiter_cannot_forge_a_collision(self):
        assert treatment_fingerprint({"a": "1|b=2"}) != treatment_fingerprint({"a": "1", "b": "2"})

    def test_forged_split_does_not_pass_equal_treatment(self):
        # End-to-end: two genuinely different splits must not certify as "equal treatment".
        a = TreatmentRecord(split_id=treatment_fingerprint(["1|2", "3"]), preprocessing_id="p", hp_budget=5)
        b = TreatmentRecord(split_id=treatment_fingerprint(["1", "2", "3"]), preprocessing_id="p", hp_budget=5)
        assert not check_equal_treatment(a, b).passed


class TestEqualTreatmentInCascade:
    def test_fair_comparison_promotes(self):
        stage = Stage.from_check("v2", lambda c: check_equal_treatment(_fair(), _fair()))
        assert run_cascade("cand", [stage]).label == "trigger_ready_research_candidate"

    def test_unfair_comparison_caps_at_validation_pending(self):
        stage = Stage.from_check("v2", lambda c: check_equal_treatment(_fair(hp_budget=1), _fair(hp_budget=1000)))
        assert run_cascade("cand", [stage]).label == "validation_pending"

    def test_reject_still_outranks_an_unfair_comparison(self):
        v2 = Stage.from_check("v2", lambda c: check_equal_treatment(TreatmentRecord(), TreatmentRecord()))
        hard = Stage("hard", lambda c: (False, {}, ["disqualified"]))
        assert run_cascade("cand", [v2, hard]).label == "reject"
