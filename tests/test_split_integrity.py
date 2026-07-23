"""S9 — temporal split-integrity detector.

Bracket test: the detector must PASS a proper forward holdout (including a purged
walk-forward split) and FAIL the shuffle-then-split specimen (CNN-LSTM).
"""

import pandas as pd

from project_money.validation import check_temporal_holdout, walk_forward_splits
from tests.specimens import causal_forward_split, cnn_lstm_shuffled_split


class TestTemporalHoldout:
    def test_forward_split_passes(self):
        train_index, test_index = causal_forward_split()
        result = check_temporal_holdout(train_index, test_index)
        assert result.passed, result.reasons

    def test_shuffled_split_caught(self):
        train_index, test_index = cnn_lstm_shuffled_split()
        result = check_temporal_holdout(train_index, test_index)
        assert not result.passed
        assert any("shuffled split" in r for r in result.reasons)

    def test_purged_walk_forward_folds_pass(self):
        """A purged/embargoed walk-forward split must not false-positive — purge
        trims the end of train, but test still lies strictly after it."""
        idx = pd.bdate_range("2020-01-01", periods=400)
        for split in walk_forward_splits(idx, n_folds=5, min_train=60, purge=5, embargo=5):
            result = check_temporal_holdout(split.train_index, split.test_index)
            assert result.passed, result.reasons

    def test_overlap_caught(self):
        idx = pd.bdate_range("2020-01-01", periods=100)
        result = check_temporal_holdout(idx[:60], idx[55:])  # 5 shared timestamps
        assert not result.passed
        assert any("BOTH train and test" in r for r in result.reasons)

    def test_empty_index_fails_closed(self):
        idx = pd.bdate_range("2020-01-01", periods=100)
        assert not check_temporal_holdout(idx[:0], idx[50:]).passed

    def test_deterministic_across_runs(self):
        train_index, test_index = cnn_lstm_shuffled_split()
        r1 = check_temporal_holdout(train_index, test_index)
        r2 = check_temporal_holdout(train_index, test_index)
        assert r1.passed == r2.passed and r1.reasons == r2.reasons

    # --- red-team regressions ---

    def test_nat_rows_fail_closed(self):
        # #9: NaT test timestamps must not be silently exempted.
        idx = pd.bdate_range("2020-01-01", periods=100)
        test_index = idx[80:].insert(0, pd.NaT)
        assert not check_temporal_holdout(idx[:80], test_index).passed

    def test_tz_mismatch_fails_closed(self):
        # #8: tz-aware vs tz-naive must fail closed, not raise.
        idx = pd.bdate_range("2020-01-01", periods=100)
        train_index = idx[:80].tz_localize("UTC")
        test_index = idx[80:]  # tz-naive, genuinely later
        result = check_temporal_holdout(train_index, test_index)
        assert not result.passed
        assert any("fail closed" in r for r in result.reasons)

    def test_unpurged_split_flagged_with_label_horizon(self):
        # #6: an unpurged forward split (zero gap) leaks label windows for horizon>0.
        idx = pd.bdate_range("2020-01-01", periods=400)
        result = check_temporal_holdout(idx[:320], idx[320:], full_index=idx, label_horizon=5)
        assert not result.passed
        assert any("purge gap" in r for r in result.reasons)

    def test_adequately_purged_split_passes_with_label_horizon(self):
        idx = pd.bdate_range("2020-01-01", periods=400)
        # drop 5 bars between train and test → gap == 5 == label_horizon
        result = check_temporal_holdout(idx[:315], idx[320:], full_index=idx, label_horizon=5)
        assert result.passed, result.reasons

    def test_label_horizon_without_full_index_fails_closed(self):
        idx = pd.bdate_range("2020-01-01", periods=400)
        result = check_temporal_holdout(idx[:315], idx[320:], label_horizon=5)
        assert not result.passed
        assert any("requires full_index" in r for r in result.reasons)

    def test_duplicate_full_index_fails_closed(self):
        # round-2 #4: a duplicate in full_index must fail closed, not crash.
        idx = pd.bdate_range("2020-01-01", periods=400)
        dup = idx.append(idx[[100]])  # one duplicated timestamp
        result = check_temporal_holdout(idx[:315], idx[320:], full_index=dup, label_horizon=5)
        assert not result.passed
        assert any("fail closed" in r for r in result.reasons)

    def test_unsorted_full_index_fails_closed(self):
        # round-2 #5: an unsorted full_index makes the position-based gap meaningless.
        idx = pd.bdate_range("2020-01-01", periods=400)
        result = check_temporal_holdout(idx[:315], idx[320:], full_index=idx[::-1], label_horizon=5)
        assert not result.passed
        assert any("fail closed" in r for r in result.reasons)
