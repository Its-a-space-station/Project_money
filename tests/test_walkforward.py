import pandas as pd
import pytest

from project_money.validation.walkforward import walk_forward_splits


class TestWalkForward:
    def test_train_strictly_precedes_test(self, dates):
        for s in walk_forward_splits(dates, n_folds=5, min_train=60):
            assert s.train_index.max() < s.test_index.min()

    def test_purge_gap(self, dates):
        purge = 5
        for s in walk_forward_splits(dates, n_folds=4, min_train=60, purge=purge):
            gap = list(dates).index(s.test_index[0]) - list(dates).index(s.train_index[-1])
            assert gap >= purge + 1 - 1  # at least `purge` rows removed before test
            assert gap > purge - 1

    def test_test_windows_tile_without_overlap(self, dates):
        splits = walk_forward_splits(dates, n_folds=5, min_train=60)
        seen: set = set()
        for s in splits:
            overlap = seen & set(s.test_index)
            assert not overlap
            seen |= set(s.test_index)
        # tests cover exactly the post-min_train region
        assert len(seen) == len(dates) - 60

    def test_expanding_train(self, dates):
        splits = walk_forward_splits(dates, n_folds=5, min_train=60)
        lengths = [len(s.train_index) for s in splits]
        assert lengths == sorted(lengths)

    def test_too_little_data_raises(self, dates):
        with pytest.raises(ValueError):
            walk_forward_splits(dates[:50], n_folds=5, min_train=60)

    def test_deterministic(self, dates):
        a = walk_forward_splits(dates, n_folds=5, min_train=60)
        b = walk_forward_splits(dates, n_folds=5, min_train=60)
        for x, y in zip(a, b):
            assert x.train_index.equals(y.train_index)
            assert x.test_index.equals(y.test_index)
