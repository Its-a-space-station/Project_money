"""Metric-plausibility alarm + cost gate — verifier items S11 and S16.

Both are **one-sided review alarms**, NOT standalone edge screens: "passed" here
means "not obviously implausible / not obviously cost-broken" — never "has an edge
and is clean." A zero-skill coin-flip forecaster passes S11 and a zero-edge no-op
passes S16. They MUST be composed with the edge-existence gates (deflated Sharpe /
multiplicity, no-lookahead, the falsification battery) before any promotion.

S11 (metric-sanity). Sustained out-of-sample directional *sign* accuracy above
~60% is implausible for liquid daily forecasting and routes to a mandatory audit
(``needs_human_review`` — a *review* disposition, not an auto-reject; a trending or
imbalanced base rate can exceed 60% with zero skill). Note it is blind to
*magnitude/payoff* leaks (a low-sign-accuracy, high-Sharpe asymmetric strategy),
so it must be paired with a payoff-plausibility alarm.

S16 (cost gate). Profitability must be cost-inclusive. Rejects: costs not modeled
at all (missing / non-positive / non-finite), a non-finite Sharpe, a cost that was
not actually applied (net Sharpe ≥ gross despite positive turnover), and an edge
that vanishes net of costs. When the primitive artifacts (weights + asset returns)
are supplied it **recomputes** gross/net/turnover via ``metrics.compute_metrics``
rather than trusting reported scalars (the "recompute, never accept a report"
doctrine); a positive-but-low reported rate is not itself grounds for rejection
(that is an instrument-liquidity judgement, not a universal gate).

Research-only: evaluates artifacts; it never acts.
"""

from __future__ import annotations

import math

from project_money.validation.invariants import CheckResult, NEEDS_HUMAN_REVIEW, REJECT
from project_money.validation.metrics import compute_metrics


def _finite(x) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def check_directional_accuracy_plausible(
    accuracy: float | None,
    *,
    max_plausible: float = 0.60,
    name: str = "OOS directional accuracy",
) -> CheckResult:
    """Flag an implausibly high directional accuracy (S11) — a review disposition.

    Fail-closed on a non-finite or out-of-[0,1] value, or one not coercible to a
    float. ``name`` must be a trusted constant (it is interpolated into the reason
    string); never source it from candidate-authored metadata.
    """
    try:
        acc = float(accuracy)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return CheckResult(
            "accuracy_plausible", False, [f"accuracy {accuracy!r} not coercible to float — fail closed"]
        )
    if not math.isfinite(acc) or not (0.0 <= acc <= 1.0):
        return CheckResult(
            "accuracy_plausible", False, [f"accuracy {accuracy!r} not a finite value in [0, 1] — fail closed"]
        )
    reasons: list[str] = []
    if acc > max_plausible:
        reasons.append(
            f"{str(name)[:80]} {acc:.4f} exceeds the plausibility bar {max_plausible:.2f} — "
            "implausible for liquid daily forecasting; mandatory audit (needs_human_review, not "
            "auto-reject) before any label"
        )
    # Implausible accuracy is a review flag, not an auto-reject; the fail-closed
    # bad-input paths above keep the default reject disposition.
    return CheckResult(
        "accuracy_plausible", not reasons, reasons, NEEDS_HUMAN_REVIEW if reasons else REJECT
    )


def check_cost_gate(
    *,
    cost_bps: float | None = None,
    sharpe_gross: float | None = None,
    sharpe_net: float | None = None,
    weights=None,
    asset_returns=None,
) -> CheckResult:
    """Require cost-inclusive evaluation (S16). See the module docstring for scope.

    Prefers recomputation from ``weights`` + ``asset_returns`` (authoritative) over
    reported scalars. Fail-closed on non-modeled / non-finite costs and Sharpes.
    """
    # 1. Costs must be modeled at all — fail closed on missing / non-positive / non-finite.
    if cost_bps is None or not _finite(cost_bps) or float(cost_bps) <= 0.0:
        return CheckResult(
            "cost_gate",
            False,
            [f"transaction cost {cost_bps!r} missing / non-positive / non-finite — costs not "
             "modeled; evaluation is not cost-inclusive"],
        )
    cb = float(cost_bps)

    reasons: list[str] = []
    turnover = None

    # 2. Authoritative recompute from primitive artifacts (never trust reported scalars).
    if weights is not None and asset_returns is not None:
        try:
            m = compute_metrics(weights, asset_returns, cost_bps=cb)
        except Exception as exc:  # malformed artifacts → fail closed, don't crash the gate
            return CheckResult(
                "cost_gate", False, [f"could not recompute metrics from artifacts: {exc} — fail closed"]
            )
        sharpe_gross, sharpe_net, turnover = m["sharpe_gross"], m["sharpe_net"], m["avg_turnover"]

    # 3. Sharpes, when present, must be finite.
    if sharpe_gross is not None and not _finite(sharpe_gross):
        reasons.append("gross Sharpe is non-finite — fail closed")
    if sharpe_net is not None and not _finite(sharpe_net):
        reasons.append("net Sharpe is non-finite — fail closed")

    if sharpe_gross is not None and sharpe_net is not None and _finite(sharpe_gross) and _finite(sharpe_net):
        sg, sn = float(sharpe_gross), float(sharpe_net)
        # 4. Cost provably not applied: net >= gross despite positive (or unknown) turnover.
        if (turnover is None or turnover > 0) and sn >= sg:
            reasons.append(
                f"net Sharpe {sn:.3f} >= gross {sg:.3f} despite positive/unknown turnover — the "
                "modeled cost was not actually applied to net returns"
            )
        # 5. Edge must survive costs.
        if sg > 0.0 and sn <= 0.0:
            reasons.append(
                f"edge vanishes net of costs (gross Sharpe {sg:.2f} > 0, net {sn:.2f} <= 0) — "
                "not a tradeable edge"
            )

    return CheckResult("cost_gate", not reasons, reasons)
