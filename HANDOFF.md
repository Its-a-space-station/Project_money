# HANDOFF.md — Project_money → research kickoff

> **Purpose.** A self-contained brief so a fresh session (or the user) can start
> the **research kickoff** without re-deriving context. It supersedes all earlier
> handoffs. Read it alongside `CLAUDE.md` (governance + doctrine), `STATE.md`
> (live snapshot), and `tasks/todo.md` + `tasks/lessons.md`.
>
> **One-line status:** information intake is complete (6 corpora), the governance
> pivot to *research-and-trading* is committed, and the project is poised to begin
> **edge discovery** — the research/validation engine, run edge-first. No execution
> build happens until a validated edge exists.

*Written: 2026-07-22. HEAD at handoff: `f9b13bc`. Branch `main`, pushed, clean.*

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
   least one strategy has actually cleared the full verification stack.** Execution
   is gated behind *a survivor*, not merely behind an authorization. If nothing
   survives, **no bot is built** — correct rejection is the intended, money-saving
   outcome. The prior Kalshi project built the bot first, found no edge, and
   stalled; we do not repeat that.

Autonomy, when it ever exists, is always **bounded / observable / stoppable**
(hard limits, kill-switches, journaling, reconciliation) and reached only through
a phased, separately-gated ladder: dry-run → paper → shadow-canary →
human-approved live → (later) bounded auto-trade.

## 2. Startup reading sequence (for the next session)

1. `CLAUDE.md` — governance (Part I) + quant-research doctrine (Part II).
2. `STATE.md` — current phase, authorized scope, approved decisions, next action.
3. `tasks/todo.md`, `tasks/lessons.md` — open work and accumulated lessons.
4. This file.
5. The six knowledge-base syntheses (see §5) as needed.
6. `docs/safety_policy.md`, `docs/broker_strategy.md` before any
   provider/execution-adjacent work.

## 3. Current state snapshot

- **Repo:** `github.com/Its-a-space-station/Project_money`, branch `main`,
  HEAD `f9b13bc`, working tree clean and pushed.
- **Tests:** `./.venv/bin/python -m pytest -q` → **170 passed**, deterministic.
  Venv at `.venv/` (Python 3.14; `pip install -e ".[dev]"`).
- **Hooks are ACTIVE** (`.claude/settings.json`): every Write/Edit runs the
  finding-promotion validator; every Bash runs the findings-write guard. Both fail
  closed. (They are target-aware — they will not false-positive on `git commit`.)
- **Git discipline:** stage explicit paths only (never `git add -A`); ask before
  commit/push; end a unit of work with `git status --short` + `git diff --stat`.

## 4. What exists — the verifier stack (built, tested, deterministic)

Under `src/project_money/` (16 test files, 170 tests):

| Module | What it does |
| --- | --- |
| `validation/invariants.py` | stage-0 invariants incl. **whole-window lookahead detector** |
| `validation/metrics.py` | multi-metric eval + **deflated Sharpe** (multiplicity-corrected; empirical cross-trial variance benchmark; raw-kurtosis guard) |
| `validation/walkforward.py` | walk-forward with **purge / embargo** |
| `validation/prequential.py` | prequential codelength vs null |
| `validation/cascade.py` | staged evaluation cascade emitting **canonical labels only** |
| `leakage/vintage.py` | data-vintage / knowledge-cutoff / formation-date auditor |
| `falsification/controls.py`, `harness.py` | known-zero controls (permutation, block, surrogate), bracket tests, nuisance sweeps |
| `ledger/hypothesis_ledger.py` | append-only JSONL trial registry (feeds DSR), **tabu memory**, repeat-failure freezes, canonical-status enforcement |
| `complexity/mdl_gate.py` | per-knob bits hurdle, permuted-null capacity, noisy-knob jitter |
| `registry/tool_registry.py`, `toolfactory/admission.py` | typed read-only tool registry; held-out tool-admission gate |
| `memory/ordering.py` | stable ids, canonical sort, order-invariant digest |

**Config layer:** four subagent roles (`.claude/agents/`: data-navigator,
strategy-analyst, research-validator, research-skeptic), two skills
(`.claude/skills/`: research-pipeline, trajectory-judge), fail-closed promotion
hooks (`hooks/validate_finding.py`, `hooks/guard_findings_bash.py`), six canonical
schemas (`schemas/`: belief_card, decision_card, evidence_record, manual_review,
postmortem, verification_debt).

**Not built (all separately gated):** provider adapters (Tiingo/FRED), any
Robinhood data or execution path, ML/forecasting models, options/cross-asset, live
scheduling.

## 5. The knowledge base — six corpora ingested, synthesized, verified

Each was read by an adversarial agent fleet, synthesized, and independently
checker-verified (maker ≠ checker) before commit. The unifying finding across all
six: **no corpus produced a validated daily-horizon edge; the verifier, not any
model, is the durable asset.**

| Doc | Corpus | Load-bearing takeaway |
| --- | --- | --- |
| `docs/agent_tooling_synthesis.md` | 38 coding-agents papers | "the verifier is the product"; agents beat benchmarks by gaming metrics (Goodhart) → skeptic role is load-bearing |
| `docs/trading_corpus_synthesis.md` | 28 trading books | 25 hypothesis families in 3 tiers; **MVP seeds = H1 momentum, H2 short-horizon reversal, H3 vol-state**; documented nulls; delisting-aware panel requirement |
| `docs/ml_shelf_integration.md` | 20 ML-engineering PDFs | verified the playbook map; **caught & fixed an anti-conservative deflated-Sharpe defect**; queued follow-ons (PSR, ROPE, conformal, CPCV/PBO, CUSUM) |
| `docs/ts_forecasting_integration.md` | 26 TS-forecasting papers | baselines-as-nulls externally evidenced (linear/naive beat deep on low-SNR); **V1–V8** verifier queue; foundation-model contamination discipline |
| `docs/graph_ml_synthesis.md` | 25 graph-ML papers | learned stock graphs = do-not-build; **W1–W6** verifier queue; distill-then-validate (symbolic) as the sanctioned ML route |
| `docs/stock_market_synthesis.md` | 73 stock-market ML/AI papers | **zero validated edges across 73 in-domain papers**; **S1–S30** verifier additions (6 new leakage-detector GAPS incl. intra-bar leakage + a calibration axis); vintage-tagged dataset catalog; live-benchmark / forward-tracking design |

**The distilled doctrine** (what the whole intake earned): baselines-as-nulls;
deflated-Sharpe / multiplicity discipline; strict leakage + vintage +
contamination checks; MDL simplicity-first; economic-mechanism requirement; and —
above all — that correct rejection of false edges is as valuable as a rare correct
promotion.

## 6. The verifier backlog (V1–V8, W1–W6, S1–S30)

Three queued sets of checker/policy additions, sequenced but not yet built. They
are catalogued in the synthesis docs (§3 of each) and are the **first research
build work**. Highest-value / novel items:

- **S1** `frozen_at` + strictly-post-timestamp **forward tracking** — the
  research-only, never-trade analogue of the live benchmarks; the contamination
  defense no after-the-fact detector can provide.
- **S6** intra-bar contemporaneous-leakage detector (a bar-granularity detector
  passes same-slot OHLC features — the batch-6 "94.76% OOS" specimen).
- **S7** non-causal decomposition leakage (EMD/DWT/correlation-graph fit on
  test data); **S8** non-causal feature construction (global scaling/spline).
- **S26** a **calibration / process-fidelity axis** (ECE) — an evaluation
  dimension the harness entirely lacks today.
- **S2/S3** model/embedder cutoff-vs-eval-window contamination gate.
- **S4/S16/S12** mandatory persistence null, cost model, min-track-record-length.
- Batch-4 **V1–V8** (window-completeness, equal-budget candidate-vs-null,
  vintage check, effect-size gate, macro/micro aggregation, threshold sweep,
  cross-metric stability, forecastability diagnostic) and batch-5 **W1–W6**
  (known-positive controls, split-key provenance, cheap-heuristic nulls,
  full-search-space DSR accounting, stratified noise probes, capacity matching).
- A **known-bad specimen fixture set** from batch 6 (MarketSenseAI time-travel,
  Mehtab-Sen intra-bar leakage, Nabipour flat-horizon R²≈1.0, CNN-LSTM shuffled
  split) — the harness *must* reject each; a pass is a hole.

## 7. THE RESEARCH KICKOFF — what "next session" does

The near-term goal is to build the engine that honestly answers **"is there an
edge?"** — and is trusted when it says *no*. Execution is out of scope until a
survivor exists (§1.3).

### 7.1 Two authorizations the user must give (neither taken unilaterally)

1. **Record the 1–4 ungating** in STATE.md's approved-decisions ledger — this
   lifts scope guards toward *research* work only: (1) deterministic MVP on cached
   data, (2) Tiingo + FRED **read-only** adapters with a point-in-time cache, (3)
   bounded strategy/factor search, (4) paper-candidate forward tracking. It does
   **not** authorize any execution path.
2. **Authorize the first build phase.** Recommended order below.

### 7.2 Recommended build sequence (edge-first)

1. **Harden the verifier (S1–S30 / V1–V8 / W1–W6).** Start with the calibration
   axis (S26), the leakage-detector GAPS (S6/S7/S8), the persistence/cost/DSR
   gates, and the **known-bad specimen fixtures** — prove the harness rejects the
   junk *before* trusting any pass. This is pure research-tooling code (already
   authorized in principle) and the credibility foundation for everything after.
2. **Read-only provider data** (Tiingo + FRED) into a **point-in-time / vintage-
   safe cache.** Respect ToS and rate limits. Delisting-aware equity/ETF panel is
   a hard requirement (batch-2 finding). Robinhood stays read-only-data-only here.
3. **The cached MVP screen** — the smallest verifiable strategy screen with
   maker/checker separation and canonical labels, run **calibration-first**:
   - **Falsification battery proven on documented nulls** (the harness must reject
     known junk before its passes mean anything).
   - **Tier-1 baselines established** (they become the null every hypothesis must
     beat): persistence, 1/N, buy-and-hold, and the relevant simple null.
   - **Seeds: H1 (momentum), H2 (short-horizon reversal), H3 (volatility-state
     conditioning)** on the delisting-aware daily equity/ETF panel. *Note the
     batch-6 refinement:* H1 is the weakest seed (most-arbitraged); **H3 /
     volatility has the best evidential support** — volatility is the one target
     the corpus repeatedly flagged as genuinely forecastable, with honest nulls
     (HAR-RV, EWMA, GARCH). Consider leading with it.
   - Every trial through the **hypothesis ledger**; every promotion through the
     **cascade + hooks**; the **research-skeptic** red-teams survivors.
4. **Paper-candidate forward tracking (S1).** Freeze survivors with a `frozen_at`
   stamp; score only on strictly-later data. This is the contamination-free track
   record that, over time, is the one credential that can't be faked.

### 7.3 The success criterion (state it plainly to the user)

The kickoff succeeds if the engine gives an **honest** answer, including "no
edge." A validated survivor unlocks the (separately-authorized) conversation about
the Robinhood ladder. No survivor means we do not build the bot — and that is the
system working, not failing.

### 7.4 What NOT to do

- Do **not** start any Robinhood/broker execution build (edge-first gate, §1.3).
- Do **not** let the assistant execute, operate live, or hold credentials (§1.1).
- Do **not** promote anything on a self-attested result (maker ≠ checker).
- Do **not** run a gross-of-cost backtest, use a non-delisting-aware universe, or
  skip the persistence/1-N null.
- Do **not** exceed the phase authorized in STATE.md; if a step would begin a new
  phase, touch credentials, or widen autonomy — **stop and ask.**

## 8. Open decisions for the user

- Record the 1–4 ungating? (research scope only)
- Authorize the first build phase, and in what order? (recommended: verifier
  hardening → read-only providers → cached MVP screen)
- Lead the MVP with **volatility / H3** (best-evidenced) or the full H1–H3 set?
- Any change to the edge-first gate or the phased ladder before research starts?

## 9. Standing constraints (unchanged, non-negotiable)

Research/validation now; the human operates any future live capital; the assistant
never executes live or holds credentials; autonomy is always bounded / observable
/ stoppable; no secrets in the repo; canonical labels in the research layer;
maker ≠ checker; explicit-path git with per-commit/push approval; validation
precedes capital; **edge before infrastructure.**

## 10. Lessons worth carrying (see `tasks/lessons.md` for all)

Lookahead detectors compare whole windows; single null-draws are flaky by
construction; enforcement boundaries are attack surfaces (fail closed, red-team
the gate); verify implemented statistics against primary sources before gating on
them (the DSR fix); a correct aggregate can hide a wrong membership (verify labels,
not just counts); the synthesis-level checker has caught a real error in three of
three batches — run it on the integrating document, not just its inputs; large,
failure-prone fan-outs want a **resumable Workflow**; and — the load-bearing one
for the kickoff — **edge before infrastructure: no execution bot until a validated
edge exists.**
