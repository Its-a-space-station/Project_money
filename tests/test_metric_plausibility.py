"""S11 (metric-plausibility) + S16 (cost gate), and the Paper 8 compound specimen.

Paper 8 is a stack of leaks; the harness must reject it through more than one
channel: the impossible OOS accuracy (S11), the cost-free backtest (S16), and the
full-sample scaler-leak (caught by the existing check_no_lookahead). Includes the
red-team regressions (NaN fail-closed, cost-not-applied, artifact recompute).
"""

from project_money.validation import (
    check_cost_gate,
    check_directional_accuracy_plausible,
    check_no_lookahead,
)
from tests.conftest import causal_momentum_signal
from tests.specimens import (
    paper8_cost_free_result,
    paper8_impossible_accuracy,
    paper8_scaler_leak_signal,
)


class TestDirectionalAccuracyPlausible:
    def test_paper8_impossible_accuracy_flagged(self):
        result = check_directional_accuracy_plausible(paper8_impossible_accuracy())
        assert not result.passed
        assert any("mandatory audit" in r for r in result.reasons)

    def test_plausible_accuracy_passes(self):
        assert check_directional_accuracy_plausible(0.53).passed

    def test_out_of_range_or_nan_fails_closed(self):
        assert not check_directional_accuracy_plausible(1.4).passed
        assert not check_directional_accuracy_plausible(None).passed
        assert not check_directional_accuracy_plausible(float("nan")).passed

    def test_non_floatable_fails_closed(self):
        # round-1 #7: a stringy metric label must fail closed, never raise.
        assert not check_directional_accuracy_plausible("high").passed


class TestCostGate:
    def test_paper8_cost_free_flagged(self):
        r = paper8_cost_free_result()
        result = check_cost_gate(
            cost_bps=r["cost_bps"], sharpe_gross=r["sharpe_gross"], sharpe_net=r["sharpe_net"]
        )
        assert not result.passed
        assert any("not cost-inclusive" in x for x in result.reasons)

    def test_edge_vanishing_net_of_costs_flagged(self):
        result = check_cost_gate(cost_bps=10.0, sharpe_gross=1.8, sharpe_net=-0.1)
        assert not result.passed
        assert any("vanishes net of costs" in x for x in result.reasons)

    def test_cost_inclusive_surviving_edge_passes(self):
        assert check_cost_gate(cost_bps=10.0, sharpe_gross=1.8, sharpe_net=1.1).passed

    # --- red-team regressions ---

    def test_nan_cost_fails_closed(self):
        # round-1 #1: NaN cost must NOT slip past the floor (nan < x is False).
        assert not check_cost_gate(
            cost_bps=float("nan"), sharpe_gross=2.0, sharpe_net=2.0
        ).passed

    def test_nan_sharpe_fails_closed(self):
        # round-1 #1: an undefined net Sharpe must fail closed, not pass.
        assert not check_cost_gate(cost_bps=10.0, sharpe_gross=2.0, sharpe_net=float("nan")).passed

    def test_cost_not_applied_flagged(self):
        # round-1 #2: net >= gross at positive cost proves the cost was not applied.
        result = check_cost_gate(cost_bps=10.0, sharpe_gross=2.4, sharpe_net=2.4)
        assert not result.passed
        assert any("not actually applied" in x for x in result.reasons)

    def test_recompute_from_artifacts_overrides_reported_scalars(self, prices):
        # round-1 #2 (doctrine): with primitive artifacts, reported Sharpes are
        # ignored — a fabricated net==gross claim cannot change the verdict.
        weights = causal_momentum_signal(prices)
        asset_returns = prices.pct_change().fillna(0.0)
        r_plain = check_cost_gate(cost_bps=10.0, weights=weights, asset_returns=asset_returns)
        r_fabricated = check_cost_gate(
            cost_bps=10.0,
            weights=weights,
            asset_returns=asset_returns,
            sharpe_gross=99.0,
            sharpe_net=99.0,
        )
        assert r_plain.passed == r_fabricated.passed
        assert r_plain.reasons == r_fabricated.reasons


class TestPaper8ScalerLeak:
    def test_full_sample_scaler_leak_caught(self, prices):
        result = check_no_lookahead(paper8_scaler_leak_signal, prices)
        assert not result.passed
        assert any("lookahead" in r for r in result.reasons)

    def test_causal_counterpart_passes(self, prices):
        assert check_no_lookahead(causal_momentum_signal, prices).passed
