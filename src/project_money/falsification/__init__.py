"""Metric-falsification harness (synthesis §4 tool 3)."""

from project_money.falsification.controls import (
    permute_returns,
    block_permute_returns,
    matched_gaussian_surrogate,
    known_zero_battery,
)
from project_money.falsification.harness import (
    bracket_test,
    nuisance_sweep,
    differential_validation,
)

__all__ = [
    "permute_returns",
    "block_permute_returns",
    "matched_gaussian_surrogate",
    "known_zero_battery",
    "bracket_test",
    "nuisance_sweep",
    "differential_validation",
]
