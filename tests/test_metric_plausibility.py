"""S11 (metric-plausibility) + S16 (cost gate), and the Paper 8 compound specimen.

Paper 8 is a stack of leaks; the harness must reject it through more than one
channel: the impossible OOS accuracy (S11), the cost-free backtest (S16), and the
full-sample scaler-leak (caught by the existing check_no_lookahead).
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
        assert any("mandatory leakage audit" in r for r in result.reasons)

    def test_plausible_accuracy_passes(self):
        assert check_directional_accuracy_plausible(0.53).passed

    def test_out_of_range_fails_closed(self):
        assert not check_directional_accuracy_plausible(1.4).passed
        assert not check_directional_accuracy_plausible(None).passed


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


class TestPaper8ScalerLeak:
    def test_full_sample_scaler_leak_caught(self, prices):
        # The scaler-leak channel of Paper 8 is a non-causal transform: the
        # existing whole-window lookahead detector must catch it.
        result = check_no_lookahead(paper8_scaler_leak_signal, prices)
        assert not result.passed
        assert any("lookahead" in r for r in result.reasons)

    def test_causal_counterpart_passes(self, prices):
        assert check_no_lookahead(causal_momentum_signal, prices).passed
