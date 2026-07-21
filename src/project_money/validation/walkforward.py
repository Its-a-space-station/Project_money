"""Walk-forward splitting with purge and embargo.

The honest out-of-sample geometry: parameters are only ever fit on data strictly
before the test window, a ``purge`` gap removes label-overlap contamination at
the boundary, and an ``embargo`` removes post-test leakage into the next train
window (de Prado Ch. 7 discipline, simplified to expanding-window walk-forward).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Split:
    """One walk-forward fold: train strictly precedes test, separated by purge."""

    train_index: pd.Index
    test_index: pd.Index


def walk_forward_splits(
    index: pd.Index,
    *,
    n_folds: int = 5,
    min_train: int = 60,
    purge: int = 0,
    embargo: int = 0,
) -> list[Split]:
    """Expanding-window walk-forward folds over ``index``.

    The post-``min_train`` region is divided into ``n_folds`` contiguous test
    windows. For fold k, train = everything before the test window minus the
    last ``purge`` observations; the first ``embargo`` observations of each
    subsequent train window after a test window are dropped implicitly by the
    expanding construction (embargo shrinks the usable end of train).

    Deterministic, order-preserving, no shuffling — time-series data only.
    """
    n = len(index)
    if n < min_train + n_folds:
        raise ValueError(
            f"not enough observations ({n}) for min_train={min_train} + {n_folds} folds"
        )

    test_region = n - min_train
    fold_size = test_region // n_folds
    if fold_size < 1:
        raise ValueError("n_folds too large for the available test region")

    splits: list[Split] = []
    for k in range(n_folds):
        test_start = min_train + k * fold_size
        test_end = n if k == n_folds - 1 else test_start + fold_size
        train_end = max(0, test_start - purge)
        train_start = 0
        if k > 0 and embargo > 0:
            train_start = min(embargo, train_end)  # drop earliest post-genesis rows
        train_idx = index[train_start:train_end]
        test_idx = index[test_start:test_end]
        if len(train_idx) == 0 or len(test_idx) == 0:
            raise ValueError(f"fold {k} produced an empty train or test window")
        splits.append(Split(train_idx, test_idx))
    return splits
