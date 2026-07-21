import math

import numpy as np
import pytest

from project_money.complexity import (
    comp_estimate,
    evidence_gain_bits,
    knob_hurdle_check,
    noisy_knob_test,
    param_bits,
)


class TestParamBits:
    def test_value(self):
        assert param_bits(1024, 2) == pytest.approx(2 * 0.5 * 10.0)

    def test_zero_params_free(self):
        assert param_bits(500, 0) == 0.0

    def test_validation(self):
        with pytest.raises(ValueError):
            param_bits(1, 2)
        with pytest.raises(ValueError):
            param_bits(100, -1)


class TestKnobHurdle:
    def test_strong_evidence_passes(self):
        # 50 nats of gain vs 2 knobs on 1000 obs (≈ 9.97 bits charge)
        result = knob_hurdle_check(-950.0, -1000.0, n_obs=1000, n_extra_params=2)
        assert result["passes"]
        assert result["net_bits"] > 0

    def test_weak_evidence_fails(self):
        # 2 nats of gain (≈ 2.9 bits) vs the same ≈ 9.97-bit charge
        result = knob_hurdle_check(-998.0, -1000.0, n_obs=1000, n_extra_params=2)
        assert not result["passes"]

    def test_gain_conversion(self):
        assert evidence_gain_bits(-990.0, -1000.0) == pytest.approx(10.0 / math.log(2.0))


class TestCompEstimate:
    def test_flexible_family_scores_on_noise(self):
        """A cherry-picking family (best of 50 random 'signals') achieves a
        decisively positive best-score on pure noise — the surcharge the gate
        must subtract. A rigid family (single fixed signal) does not."""

        def make_null(seed):
            rng = np.random.default_rng(seed)
            return rng.normal(0, 1, 250)

        def flexible_best_score(null_data):
            rng = np.random.default_rng(int(abs(null_data[0]) * 1e6) % 2**32)
            best = -np.inf
            for _ in range(50):  # the family's search over 50 variants
                sig = rng.choice([-1.0, 1.0], size=len(null_data))
                score = float(np.mean(sig * null_data) / np.std(sig * null_data) * np.sqrt(252))
                best = max(best, score)
            return best

        def rigid_score(null_data):
            return float(np.mean(null_data) / np.std(null_data) * np.sqrt(252))

        flex = comp_estimate(flexible_best_score, make_null, n_nulls=20, seed=0)
        rigid = comp_estimate(rigid_score, make_null, n_nulls=20, seed=0)
        assert flex["null_best_mean"] > 1.0  # flexibility buys Sharpe from nothing
        assert abs(rigid["null_best_mean"]) < 1.0
        assert flex["null_p95"] > rigid["null_p95"]

    def test_validation(self):
        with pytest.raises(ValueError):
            comp_estimate(lambda d: 0.0, lambda s: None, n_nulls=1)


class TestNoisyKnobTest:
    def test_knife_edge_collapses_wide_tolerance_survives(self):
        """Bracket test: a knife-edge scorer must show collapsing retention;
        a robust scorer must retain."""
        knife = lambda p: 1.0 if abs(p["x"] - 1.0) < 0.01 else 0.0
        robust = lambda p: 1.0 / (1.0 + (p["x"] - 1.0) ** 2)

        k = noisy_knob_test(knife, {"x": 1.0}, jitter_fracs=(0.1,), n_draws=40, seed=0)
        r = noisy_knob_test(robust, {"x": 1.0}, jitter_fracs=(0.1,), n_draws=40, seed=0)
        assert k["scales"][0.1]["retention"] < 0.5
        assert r["scales"][0.1]["retention"] > 0.9

    def test_deterministic(self):
        fn = lambda p: p["x"] ** 2
        a = noisy_knob_test(fn, {"x": 2.0}, seed=5)
        b = noisy_knob_test(fn, {"x": 2.0}, seed=5)
        assert a == b
