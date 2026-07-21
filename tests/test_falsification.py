import numpy as np
import pandas as pd

from project_money.falsification import (
    bracket_test,
    differential_validation,
    nuisance_sweep,
)


class TestBracketTest:
    def test_good_gate_is_trustworthy(self):
        gate = lambda x: x > 0.5
        result = bracket_test(gate, oracle_case=0.9, garbage_case=0.1)
        assert result["gate_trustworthy"]

    def test_permissive_gate_caught(self):
        """A gate that passes everything (the no-op-agent-must-fail rule)."""
        gate = lambda x: True
        result = bracket_test(gate, oracle_case=0.9, garbage_case=0.1)
        assert not result["gate_trustworthy"]
        assert not result["garbage_fails"]

    def test_dead_gate_caught(self):
        gate = lambda x: False
        result = bracket_test(gate, oracle_case=0.9, garbage_case=0.1)
        assert not result["gate_trustworthy"]
        assert not result["oracle_passes"]


class TestNuisanceSweep:
    def test_nuisance_dependent_metric_exposed(self):
        """A metric that is secretly a function of its bin count shows a wide
        range across the sweep; an honest metric shows ~none."""
        rng = np.random.default_rng(4)
        data = pd.Series(rng.normal(0, 1, 500))

        def artifact_metric(d, n_bins=10):
            return float(n_bins) / 10.0  # pure nuisance artifact

        def honest_metric(d, n_bins=10):
            return float(d.mean())  # ignores the nuisance

        sweep_a = nuisance_sweep(artifact_metric, data, {"n_bins": [5, 10, 20, 50]})
        sweep_h = nuisance_sweep(honest_metric, data, {"n_bins": [5, 10, 20, 50]})
        assert sweep_a["n_bins"]["range"] > 1.0
        assert sweep_h["n_bins"]["range"] == 0.0


class TestDifferentialValidation:
    def test_good_fix_accepted(self):
        # metric: reads 1.0 on control (artifact) and 2.0 on signal
        metric = lambda case: {"control": 1.0, "signal": 2.0}[case]
        # fix: zeroes the control, keeps most of the signal
        fixed = lambda case: {"control": 0.01, "signal": 1.8}[case]
        result = differential_validation(
            metric, fixed, "control", "signal", control_tolerance=0.05
        )
        assert result["fix_accepted"]

    def test_oversmoothing_fix_rejected(self):
        metric = lambda case: {"control": 1.0, "signal": 2.0}[case]
        oversmoothed = lambda case: {"control": 0.0, "signal": 0.1}[case]  # killed both
        result = differential_validation(
            metric, oversmoothed, "control", "signal", control_tolerance=0.05
        )
        assert not result["fix_accepted"]
        assert result["control_zeroed"] and not result["signal_retained"]

    def test_ineffective_fix_rejected(self):
        metric = lambda case: {"control": 1.0, "signal": 2.0}[case]
        noop = lambda case: {"control": 0.9, "signal": 2.0}[case]  # didn't fix control
        result = differential_validation(
            metric, noop, "control", "signal", control_tolerance=0.05
        )
        assert not result["fix_accepted"]
