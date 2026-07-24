"""V6 (threshold-sensitivity) + V7 (cross-metric ranking stability).

A conclusion that flips under a defensible knob change (a second metric, a small
threshold perturbation) is not robust → needs_human_review; malformed input or an
out-of-range knob → reject.
"""

import numpy as np

from project_money.validation import (
    Stage,
    check_cross_metric_stability,
    check_threshold_stability,
    rank_agreement,
    run_cascade,
)


class TestRankAgreement:
    def test_identical_orderings_agree(self):
        base = np.arange(20, dtype=float)
        agr = rank_agreement([base, np.sqrt(base), base * 3 + 1])  # all monotonic in the same order
        assert agr["min"] > 0.999

    def test_reversed_ordering_disagrees(self):
        base = np.arange(20, dtype=float)
        agr = rank_agreement([base, base[::-1]])
        assert agr["min"] < -0.999


class TestCrossMetricStability:
    def test_stable_ranking_passes(self):
        base = np.arange(30, dtype=float)
        assert check_cross_metric_stability({"sharpe": base, "cagr": np.sqrt(base), "hit": base * 2}).passed

    def test_reordering_is_needs_human_review(self):
        base = np.arange(30, dtype=float)
        r = check_cross_metric_stability({"m1": base, "m2": base[::-1]})
        assert not r.passed and r.disposition == "needs_human_review"
        assert any("metric-dependent" in x for x in r.reasons)

    def test_list_input_supported(self):
        base = np.arange(30, dtype=float)
        assert check_cross_metric_stability([base, base + 0.001 * base]).passed

    def test_single_metric_fails_closed(self):
        assert not check_cross_metric_stability([np.arange(30, dtype=float)]).passed

    def test_length_mismatch_fails_closed(self):
        assert not check_cross_metric_stability([np.arange(30.0), np.arange(29.0)]).passed

    def test_too_few_candidates_fails_closed(self):
        assert not check_cross_metric_stability([np.arange(4.0), np.arange(4.0)]).passed

    def test_non_finite_scores_fail_closed(self):
        base = np.arange(30, dtype=float)
        bad = base.copy()
        bad[0] = np.nan
        assert not check_cross_metric_stability([base, bad]).passed

    def test_constant_scores_fail_closed(self):
        # No metric pair has a defined ranking.
        assert not check_cross_metric_stability([np.ones(30), np.ones(30)]).passed

    def test_out_of_range_min_agreement_fails_closed(self):
        base = np.arange(30, dtype=float)
        for bad in (-0.1, 1.5, float("nan")):
            r = check_cross_metric_stability([base, base], min_agreement=bad)
            assert not r.passed and r.disposition == "reject", bad


class TestThresholdStability:
    def test_well_separated_decision_passes(self):
        scores = np.arange(20, dtype=float)  # 0..19, far from the 9.4–9.6 band
        assert check_threshold_stability(scores, [9.4, 9.5, 9.6]).passed

    def test_knife_edge_decision_is_needs_human_review(self):
        scores = np.linspace(9.4, 9.6, 20)  # clustered right in the sweep band
        r = check_threshold_stability(scores, [9.45, 9.5, 9.55])
        assert not r.passed and r.disposition == "needs_human_review"
        assert any("knife-edge" in x for x in r.reasons)

    def test_lower_is_better(self):
        scores = np.arange(20, dtype=float)
        # error metric: accept iff score <= t; well separated → stable.
        assert check_threshold_stability(scores, [9.4, 9.5, 9.6], higher_is_better=False).passed

    def test_single_threshold_fails_closed(self):
        assert not check_threshold_stability(np.arange(20.0), [9.5]).passed

    def test_too_few_candidates_fails_closed(self):
        assert not check_threshold_stability(np.arange(4.0), [1.0, 2.0]).passed

    def test_non_finite_scores_or_thresholds_fail_closed(self):
        scores = np.arange(20, dtype=float)
        assert not check_threshold_stability(np.append(scores, np.nan), [9.4, 9.6]).passed
        assert not check_threshold_stability(scores, [9.4, float("inf")]).passed

    def test_out_of_range_max_flip_frac_fails_closed(self):
        scores = np.arange(20, dtype=float)
        for bad in (-0.1, 1.5, float("nan")):
            r = check_threshold_stability(scores, [9.4, 9.6], max_flip_frac=bad)
            assert not r.passed and r.disposition == "reject", bad

    # --- red-team regressions (skeptic V6 round) ---

    def test_degenerate_sweep_fails_closed(self):
        # A1: a duplicate / all-identical sweep sweeps nothing → must not trivially PASS
        # the knife-edge (scores clustered exactly at the operating point 1.0).
        scores = np.full(20, 1.0)
        for th in ([1.0, 1.0], [1.0, 1.0, 1.0]):
            r = check_threshold_stability(scores, th)
            assert not r.passed and r.disposition == "reject", th

    def test_one_sided_sweep_is_validation_pending(self):
        # A2: a sweep entirely above every score never brackets the decision → its
        # flip==0 is vacuous, not robustness.
        scores = np.linspace(0.4, 0.6, 20)
        r = check_threshold_stability(scores, [0.9, 0.92])
        assert not r.passed and r.disposition == "validation_pending"
        assert any("never brackets" in x for x in r.reasons)

    def test_wide_margin_unanimous_is_validation_pending(self):
        # A2, intentional (not a false-positive): a sweep far BELOW every score can't
        # verify robustness at the operating point — V6 cannot tell "robustly separated"
        # from "sweep mis-placed", so it honestly returns validation_pending rather than
        # over-claiming a PASS. (A PASS should mean "verified robust at the decision".)
        scores = np.arange(50, 70, dtype=float)
        r = check_threshold_stability(scores, [9.4, 9.6])
        assert not r.passed and r.disposition == "validation_pending"


class TestStabilityInCascade:
    def test_stable_ranking_promotes(self):
        base = np.arange(30, dtype=float)
        stage = Stage.from_check("v7", lambda c: check_cross_metric_stability([base, np.sqrt(base)]))
        assert run_cascade("cand", [stage]).label == "trigger_ready_research_candidate"

    def test_metric_dependent_is_needs_human_review(self):
        base = np.arange(30, dtype=float)
        stage = Stage.from_check("v7", lambda c: check_cross_metric_stability([base, base[::-1]]))
        assert run_cascade("cand", [stage]).label == "needs_human_review"

    def test_knife_edge_threshold_is_needs_human_review(self):
        scores = np.linspace(9.4, 9.6, 20)
        stage = Stage.from_check("v6", lambda c: check_threshold_stability(scores, [9.45, 9.5, 9.55]))
        assert run_cascade("cand", [stage]).label == "needs_human_review"
