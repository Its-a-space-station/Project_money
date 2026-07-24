"""Verification backbone: invariants, metrics, walk-forward, prequential, cascade.

The gate every candidate finding passes before it may carry a canonical label
above ``validation_pending``. Three-part semantics throughout:
fail-before (the null must not already show the effect), pass-after (the
held-out gate is survived), no-regression (standing invariants stay green).
"""

from project_money.validation.invariants import (
    CheckResult,
    NEEDS_HUMAN_REVIEW,
    REJECT,
    VALIDATION_PENDING,
    FAILURE_DISPOSITIONS,
    check_data_integrity,
    check_no_lookahead,
    check_causal_transform,
    check_weights_valid,
)
from project_money.validation.equal_treatment import (
    TreatmentRecord,
    check_equal_treatment,
    treatment_fingerprint,
)
from project_money.validation.regime_robustness import check_regime_robustness
from project_money.validation.ranking_stability import (
    check_cross_metric_stability,
    check_threshold_stability,
    rank_agreement,
)
from project_money.validation.metrics import compute_metrics, deflated_sharpe
from project_money.validation.walkforward import walk_forward_splits, Split
from project_money.validation.split_integrity import check_temporal_holdout
from project_money.validation.window_completeness import (
    check_window_completeness,
    expected_window_count,
)
from project_money.validation.forecast_diagnostics import (
    r_squared,
    check_returns_not_levels,
    check_horizon_monotonicity,
)
from project_money.validation.metric_plausibility import (
    check_directional_accuracy_plausible,
    check_cost_gate,
)
from project_money.validation.calibration import (
    expected_calibration_error,
    reliability_curve,
    check_calibration,
)
from project_money.validation.prequential import prequential_log_loss, gaussian_null_forecaster
from project_money.validation.cascade import Stage, StageResult, CascadeResult, run_cascade

__all__ = [
    "CheckResult",
    "NEEDS_HUMAN_REVIEW",
    "REJECT",
    "VALIDATION_PENDING",
    "FAILURE_DISPOSITIONS",
    "TreatmentRecord",
    "check_equal_treatment",
    "treatment_fingerprint",
    "check_regime_robustness",
    "check_cross_metric_stability",
    "check_threshold_stability",
    "rank_agreement",
    "check_data_integrity",
    "check_no_lookahead",
    "check_causal_transform",
    "check_weights_valid",
    "compute_metrics",
    "deflated_sharpe",
    "walk_forward_splits",
    "Split",
    "check_temporal_holdout",
    "check_window_completeness",
    "expected_window_count",
    "r_squared",
    "check_returns_not_levels",
    "check_horizon_monotonicity",
    "check_directional_accuracy_plausible",
    "check_cost_gate",
    "expected_calibration_error",
    "reliability_curve",
    "check_calibration",
    "prequential_log_loss",
    "gaussian_null_forecaster",
    "Stage",
    "StageResult",
    "CascadeResult",
    "run_cascade",
]
