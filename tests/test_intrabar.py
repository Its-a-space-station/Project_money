"""S6 — intra-bar contemporaneous-leakage detector.

Bracket test (fail-before / pass-after): the detector must PASS a properly
causal open-time signal and FAIL the same-bar-close specimen (Mehtab & Sen
Case III). Plus a fail-before demonstration that the existing date-granularity
``check_no_lookahead`` is *blind* to this leak — the exact gap S6 closes — and a
no-false-positive guard for close-time decisions.
"""

import numpy as np
import pandas as pd
import pytest

from project_money.leakage import check_intrabar_causality
from project_money.validation import check_no_lookahead
from tests.specimens import (
    ComputeOnceIntrabarLeak,
    MemoizingIntrabarLeak,
    causal_gap_signal,
    dc_offset_squash_leak_signal,
    grid_gaming_intrabar_leak_signal,
    mehtab_sen_intrabar_leak_signal,
    noncausal_string_signal,
    nondeterministic_causal_signal,
    subatol_intrabar_leak_signal,
    synthetic_ohlc_bars,
    threshold_band_intrabar_leak_signal,
    turn_of_month_seasonality_signal,
    volume_intrabar_leak_signal,
)


class TestIntrabarCausality:
    def test_causal_open_signal_passes(self):
        bars = synthetic_ohlc_bars()
        result = check_intrabar_causality(causal_gap_signal, bars, decision_at="open")
        assert result.passed, result.reasons

    def test_mehtab_sen_case_iii_specimen_caught(self):
        bars = synthetic_ohlc_bars()
        result = check_intrabar_causality(
            mehtab_sen_intrabar_leak_signal, bars, decision_at="open"
        )
        assert not result.passed
        assert any("intra-bar" in r for r in result.reasons)

    def test_close_decision_is_not_flagged(self):
        """A signal committed at bar t's close may legitimately use that close
        (execution delayed to the next bar); nothing arrives after the close, so
        the detector must not false-positive."""
        bars = synthetic_ohlc_bars()
        result = check_intrabar_causality(
            mehtab_sen_intrabar_leak_signal, bars, decision_at="close"
        )
        assert result.passed, result.reasons

    def test_prior_bar_fields_are_causal(self):
        """Using bar t-1's high/low (fully known at t's open) is causal and must
        pass — the detector perturbs only bar t, so prior-bar use is invariant."""
        bars = synthetic_ohlc_bars()

        def prior_bar_range_signal(frame: pd.DataFrame) -> pd.Series:
            rng = (frame["high"] - frame["low"]).shift(1)
            return np.sign(rng - rng.rolling(20).mean()).fillna(0.0).rename("position")

        assert check_intrabar_causality(prior_bar_range_signal, bars, decision_at="open").passed

    def test_date_granularity_check_is_blind_to_intrabar_leak(self):
        """Fail-before: ``check_no_lookahead`` PASSES the intra-bar specimen
        because the leak is contemporaneous (same row), not cross-date — while
        the S6 detector catches it. This is the gap S6 exists to close."""
        bars = synthetic_ohlc_bars()

        def leaky_weight_panel(frame: pd.DataFrame) -> pd.DataFrame:
            pos = np.sign(frame["close"] - frame["open"]).clip(lower=0.0)
            return pos.to_frame("A")

        assert check_no_lookahead(leaky_weight_panel, bars, min_history=30).passed
        assert not check_intrabar_causality(
            mehtab_sen_intrabar_leak_signal, bars, decision_at="open"
        ).passed

    def test_missing_ohlc_columns_fail_closed(self):
        bars = synthetic_ohlc_bars().drop(columns=["close"])
        result = check_intrabar_causality(causal_gap_signal, bars)
        assert not result.passed
        assert any("missing OHLC" in r for r in result.reasons)

    def test_misaligned_output_fails_closed(self):
        bars = synthetic_ohlc_bars()

        def bad_index_signal(frame: pd.DataFrame) -> pd.Series:
            return pd.Series(0.0, index=range(len(frame)))

        result = check_intrabar_causality(bad_index_signal, bars)
        assert not result.passed
        assert any("align" in r for r in result.reasons)

    def test_deterministic_across_runs(self):
        bars = synthetic_ohlc_bars()
        r1 = check_intrabar_causality(mehtab_sen_intrabar_leak_signal, bars)
        r2 = check_intrabar_causality(mehtab_sen_intrabar_leak_signal, bars)
        assert r1.passed == r2.passed
        assert r1.reasons == r2.reasons


class TestIntrabarRedTeamRegressions:
    """Every exploit the research-skeptic used to break the first draft becomes a
    permanent must-reject (or must-diagnose-correctly) specimen."""

    def test_grid_gaming_leak_caught(self):
        # FN-1: leak that dodges a naive evenly-spaced grid; exhaustive testing
        # must still catch it on the untouched bars.
        result = check_intrabar_causality(grid_gaming_intrabar_leak_signal, synthetic_ohlc_bars())
        assert not result.passed
        assert any("intra-bar" in r for r in result.reasons)

    def test_subatol_scaled_leak_caught(self):
        # FN-3: sub-atol move but a real sign flip → the sign check must catch it.
        result = check_intrabar_causality(subatol_intrabar_leak_signal, synthetic_ohlc_bars())
        assert not result.passed
        assert any("sign" in r for r in result.reasons)

    def test_threshold_band_leak_caught(self):
        # FN-2: leak keyed inside the old ±2/5% blind band.
        result = check_intrabar_causality(threshold_band_intrabar_leak_signal, synthetic_ohlc_bars())
        assert not result.passed
        assert any("intra-bar" in r for r in result.reasons)

    def test_nondeterministic_signal_diagnosed_distinctly(self):
        # FP-1: nondeterministic-but-causal → reported as nondeterministic, not leakage.
        result = check_intrabar_causality(nondeterministic_causal_signal, synthetic_ohlc_bars())
        assert not result.passed
        assert any("nondetermin" in r.lower() for r in result.reasons)
        assert not any("intra-bar" in r for r in result.reasons)

    def test_nonnumeric_output_fails_closed(self):
        # R-1: non-numeric output must fail closed, never raise.
        result = check_intrabar_causality(noncausal_string_signal, synthetic_ohlc_bars())
        assert not result.passed

    def test_memoizing_leak_flagged_as_stateful(self):
        # Round-2 HIGH: date-keyed memoizer defeats same-index perturbation; the
        # cold-reindex statefulness probe must catch it and diagnose it distinctly.
        result = check_intrabar_causality(MemoizingIntrabarLeak(), synthetic_ohlc_bars())
        assert not result.passed
        assert any("stateful" in r for r in result.reasons)

    def test_dc_offset_squash_leak_caught(self):
        # Round-2 MEDIUM: large DC offset + sub-tolerance leak; the tight absolute
        # tolerance (no rtol) must still detect the value move.
        result = check_intrabar_causality(dc_offset_squash_leak_signal, synthetic_ohlc_bars())
        assert not result.passed

    def test_statefulness_probe_can_be_disabled(self):
        # A pure causal signal passes with the probe on or off (the probe must not
        # false-positive on a position-based causal signal).
        bars = synthetic_ohlc_bars()
        assert check_intrabar_causality(causal_gap_signal, bars, check_statefulness=True).passed
        assert check_intrabar_causality(causal_gap_signal, bars, check_statefulness=False).passed

    def test_seasonality_signal_not_false_flagged(self):
        # Round-3 Finding 1: a legitimate causal calendar/seasonality signal must
        # PASS — the cold-no-perturb baseline classifies it as calendar-dependent,
        # so the statefulness probe does not fire.
        bars = synthetic_ohlc_bars()
        result = check_intrabar_causality(turn_of_month_seasonality_signal, bars, decision_at="open")
        assert result.passed, result.reasons

    def test_volume_only_leak_caught(self):
        # Round-3 Finding 4: a volume-only intra-bar leak is caught by the absolute
        # volume probes (a zero probe flips the flag on every bar).
        result = check_intrabar_causality(volume_intrabar_leak_signal, synthetic_ohlc_bars())
        assert not result.passed

    @pytest.mark.xfail(
        strict=True,
        reason="compute-once/constant cache needs process isolation — tracked verification "
        "debt (round-3 Finding 2); base is itself the cached leak, so no compare-to-base probe "
        "can catch it",
    )
    def test_compute_once_memoizer_known_limitation(self):
        result = check_intrabar_causality(ComputeOnceIntrabarLeak(), synthetic_ohlc_bars())
        assert not result.passed
