"""Metric-plausibility alarm + cost gate — verifier items S11 and S16.

S11 (metric-sanity). Sustained out-of-sample directional accuracy above ~60% is
implausible for liquid daily forecasting and must trigger a mandatory leakage
audit. Batch-6 specimens: Paper 8 (0.96–0.99), Sectoral LSTM (~0.98), Mehtab-Sen
Case III (94.76%). This is a *plausibility alarm*, not proof of leakage — it
routes the result to an audit rather than passing it.

S16 (cost gate). Profitability must be cost-inclusive. A result evaluated with no
(or implausibly low) transaction costs, or whose edge vanishes net of costs, is at
most ``validation_pending`` and never a finding. The backtest cost model lives in
``metrics.portfolio_returns`` (linear turnover cost); this gate enforces that it
was actually applied at a realistic level and that the edge survives it.

Research-only: evaluates artifacts; it never acts.
"""

from __future__ import annotations

from project_money.validation.invariants import CheckResult


def check_directional_accuracy_plausible(
    accuracy: float | None,
    *,
    max_plausible: float = 0.60,
    name: str = "OOS directional accuracy",
) -> CheckResult:
    """Flag an implausibly high directional accuracy (S11). Fail-closed on a value
    outside [0, 1] (a malformed metric must not pass)."""
    if accuracy is None or not (0.0 <= float(accuracy) <= 1.0):
        return CheckResult(
            "accuracy_plausible", False, [f"accuracy {accuracy!r} not in [0, 1] — fail closed"]
        )
    reasons: list[str] = []
    if float(accuracy) > max_plausible:
        reasons.append(
            f"{name} {float(accuracy):.4f} exceeds the plausibility bar {max_plausible:.2f} — "
            "implausible for liquid daily forecasting; mandatory leakage audit before any label"
        )
    return CheckResult("accuracy_plausible", not reasons, reasons)


def check_cost_gate(
    *,
    cost_bps: float | None,
    sharpe_gross: float | None = None,
    sharpe_net: float | None = None,
    min_cost_bps: float = 5.0,
) -> CheckResult:
    """Require cost-inclusive evaluation (S16).

    Flags: transaction cost below ``min_cost_bps`` (per side) — evaluation is not
    cost-inclusive; and an edge that vanishes net of costs (gross Sharpe > 0 while
    net Sharpe ≤ 0). ``min_cost_bps`` defaults to a conservative 5 bps/side floor
    (Stockformer's convention is 10 bps/side).
    """
    reasons: list[str] = []
    if cost_bps is None or float(cost_bps) < min_cost_bps:
        reasons.append(
            f"transaction cost {cost_bps} bps below the {min_cost_bps} bps floor — evaluation is "
            "not cost-inclusive (a cost-free backtest is at most validation_pending)"
        )
    if sharpe_gross is not None and sharpe_net is not None:
        if float(sharpe_gross) > 0.0 and float(sharpe_net) <= 0.0:
            reasons.append(
                f"edge vanishes net of costs (gross Sharpe {float(sharpe_gross):.2f} > 0, net "
                f"{float(sharpe_net):.2f} ≤ 0) — not a tradeable edge"
            )
    return CheckResult("cost_gate", not reasons, reasons)
