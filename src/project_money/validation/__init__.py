"""Verification backbone: invariants, metrics, walk-forward, prequential, cascade.

The gate every candidate finding passes before it may carry a canonical label
above ``validation_pending``. Three-part semantics throughout:
fail-before (the null must not already show the effect), pass-after (the
held-out gate is survived), no-regression (standing invariants stay green).
"""

from project_money.validation.invariants import (
    check_data_integrity,
    check_no_lookahead,
    check_weights_valid,
)
from project_money.validation.metrics import compute_metrics, deflated_sharpe
from project_money.validation.walkforward import walk_forward_splits
from project_money.validation.prequential import prequential_log_loss, gaussian_null_forecaster
from project_money.validation.cascade import Stage, StageResult, CascadeResult, run_cascade

__all__ = [
    "check_data_integrity",
    "check_no_lookahead",
    "check_weights_valid",
    "compute_metrics",
    "deflated_sharpe",
    "walk_forward_splits",
    "prequential_log_loss",
    "gaussian_null_forecaster",
    "Stage",
    "StageResult",
    "CascadeResult",
    "run_cascade",
]
