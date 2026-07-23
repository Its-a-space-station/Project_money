# HANDOFF.md — Project_money → edge discovery

> **Purpose.** A self-contained brief so a fresh session (or the user) can pick up
> without re-deriving context. It supersedes all earlier handoffs. Read it
> alongside `CLAUDE.md` (governance + doctrine), `STATE.md` (live snapshot), and
> `tasks/todo.md` + `tasks/lessons.md`.
>
> **One-line status:** research phase 1 — **verifier hardening — is COMPLETE and
> pushed.** The harness provably rejects all five §9 known-bad specimens and every
> §6-GAP detector is built and adversarially red-teamed to convergence. The next
> phase is **edge discovery** (read-only providers → cached MVP screen), which is
> gated and **not yet started** — it needs explicit user go-ahead (CLAUDE.md §6).

*Written: 2026-07-23. HEAD at handoff: `792ff54`. Branch `main`, pushed, clean.*

---

## 1. What Project_money is (read this first)

A quantitative **research-and-trading** system. It discovers and validates
systematic strategies and, for the survivors, executes them as **automated trades
through Robinhood — operated by the human, engineered and validated by the
assistant.** The research/validation engine is both the product and the safety
rail: only strategies proven through the full verification stack ever reach
capital.

**The three constraints that govern everything (internalize these):**

1. **Division of labor** (safety_policy.md §1, the top hard constraint). The
   assistant designs, builds, tests, and validates the software. The **human
   operates live capital** — the assistant never itself places a live order, moves
   funds, flips a system to live, or handles live credentials. *This holds
   regardless of phase or precedent* (the Kalshi bot existing is not license to
   cross it).
2. **Validation before capital.** Nothing reaches live money without clearing the
   full stack: maker ≠ checker, deflated-Sharpe / multiplicity control, leakage &
   contamination audits, cost-inclusive evaluation, contamination-free forward
   tracking.
3. **Edge-first sequencing** (the Kalshi lesson, approved 2026-07-22). **No
   Robinhood execution build begins until the research engine is complete AND at
   least one strategy has actually cleared the full verification stack.** If nothing
   survives, **no bot is built** — correct rejection is the intended, money-saving
   outcome.

Autonomy, when it ever exists, is always **bounded / observable / stoppable** and
reached only through a phased, separately-gated ladder: dry-run → paper →
shadow-canary → human-approved live → (later) bounded auto-trade.

## 2. Startup reading sequence

1. `CLAUDE.md` — governance (Part I) + quant-research doctrine (Part II).
2. `STATE.md` — current phase, authorized scope, approved decisions, last checkpoint.
3. `tasks/todo.md` (esp. the **verifier-hardening review section** + the
   **Verification debt** bullet) and `tasks/lessons.md`.
4. This file.
5. `docs/stock_market_synthesis.md` §5/§6/§11 (the S1–S30 spec + the known-bad
   specimen list) if touching verifier items; the other five syntheses (§7) as needed.
6. `docs/safety_policy.md`, `docs/broker_strategy.md`, `docs/provider_strategy.md`
   before any provider/execution-adjacent work.

## 3. Current state snapshot

- **Repo:** `github.com/Its-a-space-station/Project_money`, branch `main`,
  HEAD `792ff54`, working tree clean, **pushed and in sync with `origin/main`.**
- **Tests:** `./.venv/bin/python -m pytest -q` → **263 passed, 2 xfailed**,
  deterministic across runs (~7s). Venv at `.venv/` (Python 3.14.3;
  `pip install -e ".[dev]"`). 21 test files.
  - The **2 xfails are intentional, documented isolation limits** (not failures):
    `ComputeOnceIntrabarLeak` (S6) and `FitOnceScaler` (S7/S8) — full-sample
    fit-once/compute-once stateful functions that in-process execute-and-compare
    cannot certify; the true fix is process/instance isolation (verification debt).
- **Hooks are ACTIVE** (`.claude/settings.json`): every Write/Edit runs the
  finding-promotion validator; every Bash runs the findings-write guard. Both fail
  closed and are target-aware (they will not false-positive on `git commit`).
- **Git discipline:** stage explicit paths only (never `git add -A`); ask before
  commit/push; end a unit of work with `git status --short` + `git diff --stat`.
  This session's six verifier commits (`e6bf78b`→`8339581`) plus the review-section
  doc commit (`792ff54`) are all pushed.

## 4. What research phase 1 accomplished (verifier hardening — DONE)

Committed in six feature/fix commits + one doc commit, all pushed:

- **All five §9 "must-reject" known-bad specimens are provably rejected** by the
  harness (the calibration-first milestone): Mehtab-Sen intra-bar (S6), CNN-LSTM
  shuffled split (S9), Nabipour flat-horizon (S5/S10), MarketSenseAI time-travel
  (S3, existing vintage auditor), Paper 8 compound (S11/S16 + full-sample scaler
  via `check_no_lookahead`).
- **All four §6-GAP detectors built:** S6 intra-bar, S7/S8 non-causal transforms,
  S26 calibration axis (the harness had no calibration dimension before).
- **Every detector was adversarially red-teamed to convergence** with the
  `research-skeptic` subagent (S6 ×3 rounds, S9/S5/S10 ×3, S11/S16 ×1, S7/S8+core
  ×1, S26 ×2). ~30 real holes were found and fixed — **including two CRITICAL ones
  in code that was already committed and "trusted":** the `check_no_lookahead`
  grid-gaming / untested-tail flaw (finite-horizon leaks are only visible at the
  cutoff boundary → exhaustive cutoffs now), and the S26 fixed-ECE-bar that flagged
  a *perfect* forecaster ~89% of the time at N=50 (→ bootstrap null band). **Unit
  tests missed both** — the red-team is load-bearing, not ceremony. Every exploit
  is now a permanent regression specimen in `tests/specimens.py`.

## 5. What exists — the verifier stack (built, tested, deterministic)

Backbone under `src/project_money/` (present before this phase, 170 tests):

| Module | What it does |
| --- | --- |
| `validation/invariants.py` | stage-0 invariants; `check_no_lookahead` (**now exhaustive-cutoff hardened**) + the shared `_whole_window_causal_check` core |
| `validation/metrics.py` | multi-metric eval + **deflated Sharpe** (empirical cross-trial variance benchmark; raw-kurtosis guard); the linear-turnover cost model (`portfolio_returns`) |
| `validation/walkforward.py` | walk-forward with **purge / embargo** |
| `validation/prequential.py` | prequential codelength vs a Gaussian null |
| `validation/cascade.py` | staged evaluation cascade emitting **canonical labels only** (fail → `reject`) |
| `leakage/vintage.py` | data-vintage / knowledge-cutoff / formation-date auditor (**S3**) |
| `falsification/controls.py`, `harness.py` | known-zero controls + bracket/nuisance/differential primitives |
| `ledger/hypothesis_ledger.py` | append-only JSONL trial registry (feeds DSR), tabu memory, canonical-status enforcement |
| `complexity/mdl_gate.py` | per-knob bits hurdle, permuted-null capacity, noisy-knob jitter |
| `registry/`, `toolfactory/`, `memory/` | typed read-only tool registry; held-out admission gate; stable ids / order-invariant digest |

**New detectors this phase** (each with a specimen + causal counterpart in
`tests/specimens.py`, and a dedicated test file):

| Item | Where | Public entry point(s) | Catches |
| --- | --- | --- | --- |
| **S6** intra-bar contemporaneous leakage | `leakage/intrabar.py` | `check_intrabar_causality(signal_fn, bars, decision_at=…)` | same-bar OHLC used to decide at the open (Mehtab-Sen 94.76%); execute-and-compare with a cold-reindex statefulness probe |
| **S7/S8** non-causal transform leakage | `validation/invariants.py` | `check_causal_transform(transform_fn, data)` | full-sample scaling/decomposition/spline (generalizes `check_no_lookahead` to any preprocessing/feature transform via the shared core) |
| **S9** temporal split integrity | `validation/split_integrity.py` | `check_temporal_holdout(train_index, test_index, full_index=…, label_horizon=…)` | shuffle-then-split interleaving (CNN-LSTM); fail-closed on NaT/tz/dup/unsorted |
| **S5/S10** forecast diagnostics | `validation/forecast_diagnostics.py` | `check_returns_not_levels(…)`, `check_horizon_monotonicity(…)`, `r_squared` | level-fit mirage / repackaged persistence (three-regime, integratedness-inferred); flat/inverted horizon-error curve (Nabipour) |
| **S11/S16** metric plausibility + cost | `validation/metric_plausibility.py` | `check_directional_accuracy_plausible(…)`, `check_cost_gate(…, weights=…, asset_returns=…)` | implausible OOS accuracy; cost-free/edge-vanishes-net (recomputes from artifacts) |
| **S26** calibration axis | `validation/calibration.py` | `check_calibration(pred_probs, outcomes)`, `expected_calibration_error`, `reliability_curve` | miscalibrated probabilities via per-bin studentized test + family-wise bootstrap null |

**Config layer (unchanged):** four subagent roles (`.claude/agents/`:
data-navigator, strategy-analyst, research-validator, **research-skeptic** — use it
to red-team every new gate), two skills (`.claude/skills/`: research-pipeline,
trajectory-judge), fail-closed promotion hooks, six canonical schemas (`schemas/`).

**Still NOT built (all separately gated):** provider adapters (Tiingo/FRED), any
Robinhood data or execution path, ML/forecasting models, options/cross-asset, live
scheduling.

## 6. Verification debt & remaining verifier items (do not rediscover these)

Tracked, honest residuals (see `tasks/todo.md` "Verification debt" bullet):

- **Adversarial statefulness needs isolation.** In-process execute-and-compare
  (S6, S7/S8, `check_no_lookahead`) cannot certify a full-sample fit-once/compute-once
  `signal_fn`/transform. The two xfails document this; the real fix is a
  subprocess/fresh-instance harness (or requiring a *factory* not a fitted object).
- **`max_test_bars` fast path** (S6 and the causal core) is a best-effort screen —
  a strided subset is in principle recomputable; **exhaustive (the default) is the
  trustworthy mode.**
- **Review-disposition wiring.** S11, S10, the S5 returns bar, and the S16
  rate-advisory are `needs_human_review` flags, but `CheckResult` is binary and
  `run_cascade` maps any fail → `reject`. **When these get wired into a cascade,
  give them a machine-readable review disposition — do NOT register them as
  rejecting stages** (else legitimate strategies are hard-rejected).
- **One-sided alarms must be composed.** S11/S16/S26 pass a trivial null; they are
  never standalone edge screens — compose with deflated-Sharpe, `check_no_lookahead`,
  and (for calibration) `prequential_log_loss`.
- **S5 delegates contemporaneous leaks** to the one-bar execution lag + S6 +
  walk-forward. **TODO: a dedicated red-team confirming that path actually covers
  autocorrelated/level targets** (skeptic-recommended, not yet done).
- **Inherent limits:** S5 φ<0.97 abstain-regime honesty gap (not capital-at-risk);
  S26 sub-finest-bin anti-calibration + small-N power loss.

Remaining verifier items (lower-priority / MVP-coupled, **not** started): **S1**
`frozen_at` forward tracking (comes with the MVP), **S2** LLM-feature vintage
extension, **S18** universe/survivorship point-in-time audit (Paper 8's last
channel), **S12** min-track-record-length, **S4** persistence-null cascade stage,
and the **V1–V8 / W1–W6** queues (largely overlap what's built — dedupe before
building).

## 7. The knowledge base — six corpora ingested, synthesized, verified

Unifying finding: **no corpus produced a validated daily-horizon edge; the
verifier, not any model, is the durable asset.** Docs: `agent_tooling_synthesis`
(38 coding papers — "verifier is the product"), `trading_corpus_synthesis` (28
books — 25 hypothesis families; MVP seeds H1/H2/H3; delisting-aware panel required),
`ml_shelf_integration` (20 PDFs — fixed the DSR defect), `ts_forecasting_integration`
(26 papers — V1–V8; baselines-as-nulls), `graph_ml_synthesis` (25 papers — W1–W6;
graph-ML = do-not-build), `stock_market_synthesis` (73 papers — **zero validated
edges**; the S1–S30 spec + the §9 known-bad specimens the harness now rejects).

## 8. NEXT PHASE — edge discovery (gated; not started)

Goal: build the smallest engine that honestly answers **"is there an edge?"** and
is trusted when it says *no*. **Beginning provider adapters is a new build step
that requires explicit user go-ahead** (CLAUDE.md §6) — it is authorized in scope
by the 1–4 ungating but not yet started; confirm before writing provider code.

Recommended sequence (edge-first; verifier hardening is already done):

1. **Read-only provider data** — Tiingo + FRED into a **point-in-time / vintage-safe
   cache.** Respect ToS + rate limits; **no secrets in the repo** (API keys are
   human-supplied env vars at runtime — stop and ask how they're provided). A
   **delisting-aware equity/ETF panel is a hard requirement** (batch-2 finding).
   Robinhood stays read-only-data-only, and even that is a later, separate gate.
2. **The cached MVP screen** — the smallest verifiable strategy screen with
   maker/checker separation and canonical labels, run **calibration-first**:
   - Prove the falsification battery on the documented nulls first (the harness
     already rejects the §9 specimens — build on that).
   - Establish Tier-1 baselines as the null every hypothesis must beat:
     persistence, 1/N, buy-and-hold, and the relevant simple null.
   - Seeds **H1 momentum / H2 short-horizon reversal / H3 volatility-state.**
     *Batch-6 refinement:* H1 is weakest (most-arbitraged); **H3 / volatility has
     the best evidential support** (HAR-RV, EWMA, GARCH as honest nulls) — consider
     leading with it. Cost-inclusive always (use `check_cost_gate` / the cost model).
   - Every trial through the **hypothesis ledger**; every promotion through the
     **cascade + hooks + `research-validator`**; **`research-skeptic` red-teams any
     survivor** before it is believed.
3. **Paper-candidate forward tracking (S1)** — freeze survivors with a `frozen_at`
   stamp; score only on strictly-later data. The one credential that can't be faked.

**What NOT to do:** start any Robinhood/broker execution build (edge-first gate);
let the assistant execute / operate live / hold credentials; promote on a
self-attested result (maker ≠ checker); run a gross-of-cost backtest or a
non-delisting-aware universe; wire a review-disposition check as a hard cascade
reject; or exceed the phase authorized in `STATE.md` — if a step would begin a new
phase, touch credentials, or widen autonomy, **stop and ask.**

## 9. Open decisions for the user

- Proceed to **edge discovery** (providers → MVP) or finish long-tail verifier
  items (S1/S2/S18, V/W dedup) first?
- Confirm go-ahead to write **read-only provider adapters** (Tiingo/FRED) — and how
  are the API keys supplied at runtime (env var names)?
- Lead the MVP with **volatility / H3** (best-evidenced) or the full H1–H3 set?
- Any change to the edge-first gate or the phased ladder before edge discovery starts?

## 10. Standing constraints (unchanged, non-negotiable)

Research/validation now; the human operates any future live capital; the assistant
never executes live or holds credentials; autonomy is always bounded / observable /
stoppable; no secrets in the repo; canonical labels in the research layer;
maker ≠ checker; explicit-path git with per-commit/push approval; validation
precedes capital; **edge before infrastructure.**

## 11. Lessons worth carrying (see `tasks/lessons.md` for all — 23 dated entries)

The load-bearing lessons from this phase, distilled: (1) execute-and-compare assumes a **pure**
`signal_fn` — state defeats it, needs isolation; (2) **finite-horizon leaks are
only visible at the cutoff boundary → use exhaustive cutoffs**, never a sparse
recomputable grid (this bit the "trusted" `check_no_lookahead`); (3) a verifier's
own knobs (sampling, perturbation width, tolerance) are attack surfaces; (4) **gate
against the honest null, not a fixed threshold**, and never let self-attested
metadata disable a check; (5) NaN fails a naive numeric gate **open** — sibling
gates must fail the same (closed) direction; (6) **recompute metrics from
artifacts, never trust reported scalars**; (7) one-sided alarms aren't standalone
screens — compose them; (8) binary pass/fail conflates **reject vs
needs_human_review**; (9) for a finite-sample-biased metric use a **bootstrap null
band** + a max-over-cells companion, not a fixed constant. Older load-bearing ones:
verify implemented statistics against primary sources before gating; run the
synthesis-level checker on the integrating document; large failure-prone fan-outs
want a resumable Workflow; and — above all — **edge before infrastructure.**

**The meta-lesson of this phase:** continued adversarial red-teaming pays off even
on code that is already committed and green. Do it for every new gate.
