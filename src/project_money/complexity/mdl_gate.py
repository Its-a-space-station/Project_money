"""MDL complexity budgeting — complexity must be earned in bits.

Implements the theory cluster's operational rules (synthesis §3.6, §6.4):

- ``param_bits``: each tuned real parameter costs ~ (1/2) log2(n) bits at the
  optimal 1/sqrt(n) discretization (Grünwald Eq. 2.9). An added knob is
  admissible only if it buys more in-sample evidence than it costs.
- ``comp_estimate``: a family's *real* capacity is how well it fits pure noise
  — fit the family to permuted/surrogate null histories and summarize the
  score it achieves there (the empirical COMP / "fits-pure-noise" surcharge).
- ``noisy_knob_test``: Hinton's bits-back pricing operationalized — jitter
  fitted parameters and measure performance decay; a strategy that collapses
  under small perturbation encodes many bits (knife-edge precision) and is a
  likely false discovery.

Research-only; evaluates artifacts, never acts.
"""

from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np


def param_bits(n_obs: int, n_params: int) -> float:
    """Description-length charge (bits) for ``n_params`` tuned real parameters
    fit on ``n_obs`` observations: n_params * (1/2) * log2(n_obs)."""
    if n_obs < 2:
        raise ValueError("n_obs must be >= 2")
    if n_params < 0:
        raise ValueError("n_params must be >= 0")
    return n_params * 0.5 * math.log2(n_obs)


def evidence_gain_bits(loglik_candidate: float, loglik_null: float) -> float:
    """In-sample evidence gain in bits: (ll_candidate - ll_null) / ln 2.
    Log-likelihoods in nats."""
    return (loglik_candidate - loglik_null) / math.log(2.0)


def knob_hurdle_check(
    loglik_candidate: float,
    loglik_null: float,
    *,
    n_obs: int,
    n_extra_params: int,
) -> dict[str, float | bool]:
    """The per-knob hurdle: extra parameters are admissible only if the
    evidence gain exceeds their description-length charge (the BIC-floor rule;
    it *undercounts* flexible families — pair with ``comp_estimate``)."""
    gain = evidence_gain_bits(loglik_candidate, loglik_null)
    charge = param_bits(n_obs, n_extra_params)
    return {
        "evidence_gain_bits": gain,
        "param_charge_bits": charge,
        "net_bits": gain - charge,
        "passes": gain > charge,
    }


def comp_estimate(
    family_best_score_fn: Callable[[Any], float],
    null_generator: Callable[[int], Any],
    *,
    n_nulls: int = 50,
    seed: int = 0,
) -> dict[str, float]:
    """Empirical parametric-complexity surcharge: how well does this strategy
    family score on data with no structure?

    ``family_best_score_fn(null_data)`` must run the family's full fitting
    procedure (the same search that will be run on real data — including any
    parameter tuning) and return its best achieved score on that null.
    ``null_generator(seed)`` produces one null dataset.

    Returns the null-score distribution summary. The family's score on real
    data is only meaningful in excess of ``null_p95`` — scores below it are
    what pure noise plus this family's flexibility already delivers.
    """
    if n_nulls < 2:
        raise ValueError("n_nulls must be >= 2")
    scores = np.array(
        [float(family_best_score_fn(null_generator(seed + i))) for i in range(n_nulls)]
    )
    return {
        "null_best_mean": float(scores.mean()),
        "null_best_std": float(scores.std(ddof=1)),
        "null_p95": float(np.quantile(scores, 0.95)),
        "null_max": float(scores.max()),
        "n_nulls": float(n_nulls),
    }


def noisy_knob_test(
    score_fn: Callable[[dict[str, float]], float],
    fitted_params: dict[str, float],
    *,
    jitter_fracs: tuple[float, ...] = (0.05, 0.10, 0.25),
    n_draws: int = 20,
    seed: int = 0,
) -> dict[str, Any]:
    """Perturbation-priced parameter precision (Hinton's noisy weights).

    Each fitted parameter is jittered multiplicatively by Gaussian noise of
    relative scale ``f`` (zero-valued params jittered additively on unit
    scale); ``score_fn`` is re-evaluated ``n_draws`` times per scale.

    Output per scale: mean jittered score and retention vs the point estimate.
    A candidate whose score collapses at small jitter is knife-edge —
    high description length, likely overfit. The tolerated jitter scale is the
    strategy's implied parameter precision.
    """
    rng = np.random.default_rng(seed)
    base = float(score_fn(fitted_params))
    out: dict[str, Any] = {"base_score": base, "scales": {}}
    for f in jitter_fracs:
        draws = []
        for _ in range(n_draws):
            jittered = {}
            for k, v in fitted_params.items():
                if v == 0.0:
                    jittered[k] = float(rng.normal(0.0, f))
                else:
                    jittered[k] = float(v * (1.0 + rng.normal(0.0, f)))
            draws.append(float(score_fn(jittered)))
        arr = np.array(draws)
        retention = float(arr.mean() / base) if base != 0 else float("nan")
        out["scales"][f] = {
            "mean_score": float(arr.mean()),
            "std_score": float(arr.std(ddof=1)),
            "retention": retention,
        }
    return out
