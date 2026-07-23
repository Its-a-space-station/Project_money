"""Temporal split-integrity check — verifier item S9.

Detects the shuffle-then-split leak: rows of a serially-correlated series
permuted *before* the train/test partition, so test rows sit temporally adjacent
to — or before — train rows and the model effectively trains on its own future.
The motivating specimen is the batch-6 "CNN-LSTM (shuffled series)" paper.

A valid time-series holdout is a *forward* holdout: every test timestamp is
strictly later than every train timestamp. Any timestamp shared by both, or any
test timestamp at/before the last train timestamp, is interleaving — the
shuffled-split fingerprint.

**Scope (do not over-read).** This validates *interleaving/overlap* only. It does
NOT verify purge/embargo *adequacy*: an unpurged forward split (test starts one
bar after train) passes here even though, for a label horizon h>0, the last h
train labels are built from data inside the test window. Purge/embargo adequacy is
enforced at split *construction* (see ``walk_forward_splits``' purge/embargo). It
can also be verified here by supplying ``label_horizon`` together with
``full_index`` (the complete ordered index the split was drawn from) — the purged
bars are absent from train and test, so the gap is only measurable against it.

Research-only: evaluates an artifact; it never acts.
"""

from __future__ import annotations

import pandas as pd

from project_money.validation.invariants import CheckResult


def check_temporal_holdout(
    train_index, test_index, *, full_index=None, label_horizon: int = 0
) -> CheckResult:
    """Audit a single train/test partition for temporal integrity.

    Flags (each recorded, none silently dropped): NaT/NaN entries or incomparable
    indices (fail-closed), timestamps present in both windows, and test timestamps
    at or before the last train timestamp (interleaved / shuffled split). When
    ``label_horizon > 0``, also requires a purge gap of at least ``label_horizon``
    observations between the last train timestamp and the first test timestamp,
    measured against ``full_index`` (required in that mode — the purged bars are in
    neither train nor test, so the gap cannot be counted from them alone).
    Accepts any comparable index (DatetimeIndex, integer positions, ...).
    """
    train_index = pd.Index(train_index)
    test_index = pd.Index(test_index)
    if len(train_index) == 0 or len(test_index) == 0:
        return CheckResult("temporal_holdout", False, ["empty train or test index"])
    if train_index.hasnans or test_index.hasnans:
        return CheckResult(
            "temporal_holdout", False, ["train/test index contains NaT/NaN — fail closed"]
        )

    reasons: list[str] = []

    try:
        overlap = train_index.intersection(test_index)
        train_max = train_index.max()
        early = test_index[test_index <= train_max]
    except TypeError as exc:
        return CheckResult(
            "temporal_holdout",
            False,
            [f"incomparable indices (e.g. tz-aware vs tz-naive): {exc} — fail closed"],
        )

    if len(overlap) > 0:
        reasons.append(f"{len(overlap)} timestamp(s) appear in BOTH train and test")

    if len(early) > 0:
        reasons.append(
            f"{len(early)} of {len(test_index)} test timestamps fall at/before the last "
            f"train timestamp ({train_max!s}) — interleaved/shuffled split (temporal leakage)"
        )
    elif label_horizon > 0:
        # Purge gap is only measurable against the full original index (the purged
        # bars are absent from both train and test).
        if full_index is None:
            reasons.append(
                "label_horizon check requires full_index (the purged bars are in neither "
                "train nor test) — cannot verify purge gap (fail closed)"
            )
        else:
            full = pd.Index(full_index)
            # The position-based gap is only meaningful on a unique, sorted,
            # non-null index; otherwise fail closed rather than fabricate a gap.
            if full.hasnans or not full.is_unique or not full.is_monotonic_increasing:
                reasons.append(
                    "full_index must be non-null, unique, and monotonically increasing to "
                    "measure the purge gap — fail closed"
                )
            else:
                tr_pos = int(full.get_indexer([train_max])[0])
                te_pos = int(full.get_indexer([test_index.min()])[0])
                if tr_pos < 0 or te_pos < 0:
                    reasons.append("train_max/test_min not found in full_index — fail closed")
                else:
                    gap = te_pos - tr_pos - 1
                    if gap < label_horizon:
                        reasons.append(
                            f"purge gap {gap} < label_horizon {label_horizon} — last train labels "
                            "overlap the test window (embargo/purge leakage)"
                        )

    return CheckResult("temporal_holdout", not reasons, reasons)
