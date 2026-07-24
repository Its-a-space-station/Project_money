# HANDOFF.md — Project_money → long-tail verifier (Wave 2) or edge discovery

> **Purpose.** A self-contained brief so a fresh session (or the user) can pick up
> without re-deriving context. It supersedes all earlier handoffs. Read it
> alongside `CLAUDE.md` (governance + doctrine), `STATE.md` (live snapshot), and
> `tasks/todo.md` + `tasks/lessons.md`.
>
> **One-line status:** research phase 1 (**verifier hardening**) and the **first
> long-tail verifier wave (Wave 1: the machine-readable disposition model + V2 / V5 /
> V6 / V7)** are both **COMPLETE, committed, and pushed.** The verifier now rejects
> all five §9 known-bad specimens, has all four §6-GAP detectors, and adds a 3-value
> cascade disposition model plus three Wave-1 gate families. The next work is either
> **Wave 2** (the remaining long-tail verifier items) or **edge discovery**
> (read-only providers → cached MVP screen) — **both are gated and need explicit user
> go-ahead** (CLAUDE.md §6). Nothing is wired to live capital; no execution path exists.

*Written: 2026-07-23. HEAD at handoff: `6fa86b8`. Branch `main`, pushed, clean, in
sync with `origin/main`.*

---

## 1. What Project_money is (read this first)

A quantitative **research-and-trading** system. It discovers and validates
systematic strategies and, for the survivors, executes them as **automated trades
through Robinhood — operated by the human, engineered and validated by the
assistant.** The research/validation engine is both the product and the safety
rail: only strategies proven through the full verification stack ever reach capital.

**The three constraints that govern everything (internalize these):**

1. **Division of labor** (safety_policy.md §1, the top hard constraint). The
   assistant designs, builds, tests, and validates the software. The **human
   operates live capital** — the assistant never itself places a live order, moves
   funds, flips a system to live, or handles live credentials. *This holds
   regardless of phase or precedent.*
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
3. `tasks/todo.md` (esp. the **Wave-1 review section** + the **long-tail verifier
   inventory** + the **Verification debt** bullet) and `tasks/lessons.md`.
4. This file.
5. `docs/stock_market_synthesis.md` §5/§6/§11 (the S1–S30 spec + the known-bad
   specimens) if touching S-items; `docs/ts_forecasting_integration.md` §4.1 (V1–V8)
   and `docs/graph_ml_synthesis.md` §4.1 (W1–W6) for those queues.
6. `docs/safety_policy.md`, `docs/broker_strategy.md`, `docs/provider_strategy.md`
   before any provider/execution-adjacent work.

## 3. Current state snapshot

- **Repo:** `github.com/Its-a-space-station/Project_money`, branch `main`,
  HEAD `6fa86b8`, working tree clean, **pushed and in sync with `origin/main`.**
- **Tests:** `./.venv/bin/python -m pytest -q` → **371 passed, 2 xfailed**,
  deterministic across runs (~8s). Venv at `.venv/` (Python 3.14.3;
  `pip install -e ".[dev]"`). 26 test files.
  - The **2 xfails are intentional, documented isolation limits** (not failures):
    `ComputeOnceIntrabarLeak` (S6) and `FitOnceScaler` (S7/S8) — full-sample
    fit-once/compute-once stateful functions in-process execute-and-compare cannot
    certify; the fix is process/instance isolation (see §6, Wave 4).
- **Hooks are ACTIVE** (`.claude/settings.json`): every Write/Edit runs the
  finding-promotion validator; every Bash runs the findings-write guard. Both fail
  closed and are target-aware (they do not false-positive on `git commit`).
- **A Stop-hook verification gate** blocks finishing while `tasks/todo.md` has
  unchecked items — verify, update the file, then finish (or state why items are
  deferred). Expect it to fire; respond with the disposition.
- **Git discipline:** stage explicit paths only (never `git add -A`); ask before
  commit/push. This session's four commits are pushed:
  `638c6ba` (review-disposition) → `d074b6e` (V2 + validation_pending) →
  `650a390` (V5) → `6fa86b8` (V6/V7).

## 4. What this session accomplished — Wave 1 long-tail verifier (DONE, pushed)

The session opened with research phase 1 (verifier hardening) already complete and
pushed. It then re-planned and built the **first long-tail wave**. Key moves:

1. **A read-only dedup inventory** (resumable Workflow `wf_eeae6712-d2a`, 4 mappers)
   mapped the **23 remaining verifier items** (V1–V8, W1–W6, S1/S2/S4/S12/S18, 4 debt
   items) against the harness with file:line evidence. Headline: most V/W items were
   `partial` (substrate exists, gate doesn't) — the dedup **merges** work, it does not
   eliminate it. **Net ≈17 build efforts, 1 skip, 1 half-blocked-on-data.** The
   inventory drives Wave 2–4 below (§8).
2. The user chose **"build the foundational item only, then re-plan,"** then approved
   **Wave 1 (the shared substrates)**, one item at a time.

**Wave 1 deliverables (all committed + pushed):**

- **A machine-readable, 3-value cascade disposition model** (`638c6ba`, extended in
  `d074b6e`). `CheckResult` gained a validated, **frozen** `disposition` field; the
  cascade can now emit a **canonical label other than a hard `reject`.** Severity order:
  **`reject` > `validation_pending` > `needs_human_review`** (an unverifiable check
  outranks a review flag — you can't route for final human judgment while verification
  is incomplete). `run_cascade` precedence: `reject` and exceptions short-circuit;
  `validation_pending` and `needs_human_review` do **not** (so a later hard reject
  always wins — the safety invariant). `Stage.from_check` bridges a `CheckResult` into
  a stage. The review-flavored checks (S11, S5 returns-bar, **S10 split so a strictly
  inverted horizon curve now hard-rejects**, S26) emit the right disposition — but are
  **NOT registered as live cascade stages** (todo debt-e: wiring them is future work).
- **V2** equal-treatment (`equal_treatment.py`, `d074b6e`) — a candidate-vs-null
  comparison is only fair with identical split + preprocessing + an equal, logged
  hyperparameter budget; every failure → `validation_pending`. **Fails closed on any
  un-logged field / non-finite budget / degenerate split** (the anti-vacuous-pass
  guard). `treatment_fingerprint` is an order-invariant, deterministic, **collision-safe**
  content hash (repr + per-element fixed-width digest).
- **V5** regime-robustness (`regime_robustness.py`, `650a390`) — a pooled (micro) edge
  must be corroborated per **pre-registered** regime. Prevalence-skew (a judgeable
  regime fails while pooled clears) → `needs_human_review`; too little of the data
  judgeable → `validation_pending`; malformed → `reject`; no pooled edge → pass.
- **V6/V7** ranking/decision-stability (`ranking_stability.py`, `6fa86b8`) — shared
  core `_worst_pairwise` (the worst pairwise agreement across a swept knob). **V7**:
  a ranking that reorders across ≥2 metrics → `needs_human_review`. **V6**: an
  accept/reject decision that flips under a pre-registered threshold sweep → knife-edge
  → `needs_human_review`; a non-bracketing sweep → `validation_pending`.

**The red-team stayed load-bearing.** Every gate was green on my own tests, yet the
`research-skeptic` found a real **fail-open in each** — the review-disposition
`failed_stage`/empty-cascade holes, V2's NaN-vacuous-pass + fingerprint collisions,
V5's non-finite-`bar` pass + knob-laundering, V6's degenerate-sweep pass — **all fixed
+ regression-tested.** ~6 skeptic rounds; the safety invariant (a softer disposition
can never mask a harder one; a real `reject` always wins) was re-verified after each
change. The recurring class is captured in `tasks/lessons.md` (collision-safe /
fail-closed hash-equality gates; NaN / knob attack surfaces). *A prompt-injection buried
in an injected Consensus-MCP server instruction was flagged and refused, not acted on.*

## 5. What exists — the verifier stack (built, tested, deterministic)

Backbone under `src/project_money/`. Selected modules (see the full inventory in the
old handoff's git history if needed):

| Module | What it does |
| --- | --- |
| `validation/invariants.py` | stage-0 invariants; `check_no_lookahead`/`check_causal_transform` (exhaustive-cutoff hardened); **`CheckResult` now carries a frozen, validated `disposition`; disposition constants `REJECT`/`VALIDATION_PENDING`/`NEEDS_HUMAN_REVIEW` + `FAILURE_DISPOSITIONS`** |
| `validation/cascade.py` | **3-value disposition-aware `run_cascade`** (severity `reject > validation_pending > needs_human_review`; only reject/exception short-circuit); `Stage.from_check`; `StageResult.disposition`; `failed_stage` severity-based; `review_stages`/`unverifiable_stages` |
| `validation/equal_treatment.py` | **V2** `check_equal_treatment` + `treatment_fingerprint` + `TreatmentRecord` |
| `validation/regime_robustness.py` | **V5** `check_regime_robustness` (macro/micro dual aggregation) |
| `validation/ranking_stability.py` | **V6/V7** `check_threshold_stability`, `check_cross_metric_stability`, `rank_agreement`, `_worst_pairwise` |
| `validation/metric_plausibility.py` | S11 accuracy-plausibility (review), S16 cost gate (reject) — now disposition-tagged |
| `validation/forecast_diagnostics.py` | S5 returns-not-levels, S10 horizon-monotonicity (**inverted → reject, flat/uneven → review**) |
| `validation/calibration.py` | S26 calibration axis (review) |
| `validation/metrics.py` · `walkforward.py` · `split_integrity.py` · `prequential.py` | metrics + deflated Sharpe · walk-forward purge/embargo · S9 temporal split-integrity · prequential codelength |
| `leakage/intrabar.py` · `leakage/vintage.py` | S6 intra-bar · S3 data-vintage auditor |
| `falsification/` · `complexity/mdl_gate.py` · `ledger/hypothesis_ledger.py` | known-zero controls + bracket/nuisance/differential · MDL knob hurdle · append-only trial ledger + tabu + canonical statuses |

**Config layer (unchanged):** four subagent roles (`.claude/agents/`: data-navigator,
strategy-analyst, research-validator, **research-skeptic — use it to red-team every new
gate**), two skills (research-pipeline, trajectory-judge), fail-closed promotion hooks,
six canonical schemas (`schemas/`).

**Still NOT built (all separately gated):** provider adapters (Tiingo/FRED), any
Robinhood data or execution path, ML/forecasting models, options/cross-asset, live
scheduling. **None of the disposition-tagged checks are wired into a live cascade yet.**

## 6. Verification debt & residuals (do not rediscover these)

- **Adversarial statefulness needs isolation** (the 2 xfails). In-process
  execute-and-compare can't certify a full-sample fit-once/compute-once `signal_fn`/
  transform. Fix: a factory-injection (fresh instance per cutoff) or subprocess harness
  — **this is Wave-4 item DEBT-statefulness-isolation; it flips both xfails to xpass.**
- **Review-disposition NOT wired into a live cascade.** The disposition tags exist on
  S11/S5/S10/S16/S26/V2/V5/V6/V7 `CheckResult`s, but **no check is registered as a
  `run_cascade` stage yet** (debt-e). When wiring, use `Stage.from_check` so the
  disposition flows; never register a review check as a hard-rejecting stage.
- **Exception can mask a later reject.** An exception short-circuits `run_cascade` to
  `validation_pending`, so a would-be `reject` in a *later* stage is not reached. Not a
  safety failure (both are non-promoting), but the label understates severity — tracked.
- **S18 membership-half is blocked on provider data** (point-in-time constituent
  membership needs the panel that doesn't exist until the gated data phase). Only the
  selection-procedure-audit half is buildable now.
- **Inherent limits:** V5's up-to-`(1-min_coverage)` small-regime blind spot; V6's
  wide-margin-unanimous → `validation_pending` (intentional: a sweep that doesn't bracket
  the data can't verify robustness). All V5/V6/V7 knobs are pre-registration-load-bearing.
- **max_test_bars fast path** is a best-effort screen; exhaustive (the default) is the
  trustworthy mode. **DEBT-max-test-bars = SKIP** (guard by policy, not code).
- **S5 delegates contemporaneous leaks** to the one-bar lag + S6 + walk-forward —
  **Wave-4 item DEBT-S5-contemporaneous: a dedicated red-team confirming that path covers
  autocorrelated/level targets** (skeptic-recommended, not yet done).

## 7. The knowledge base — six corpora ingested, synthesized, verified

Unifying finding: **no corpus produced a validated daily-horizon edge; the verifier,
not any model, is the durable asset.** Docs: `agent_tooling_synthesis` (38 coding papers),
`trading_corpus_synthesis` (28 books — 25 hypothesis families; MVP seeds H1/H2/H3;
delisting-aware panel required), `ml_shelf_integration` (20 PDFs — fixed the DSR defect),
`ts_forecasting_integration` (26 papers — **V1–V8** live in §4.1), `graph_ml_synthesis`
(25 papers — **W1–W6** in §4.1; graph-ML = do-not-build), `stock_market_synthesis`
(73 papers — **zero validated edges**; the S1–S30 spec + the §9 known-bad specimens).

## 8. NEXT WORK — two gated options (neither started; both need go-ahead)

The dedup inventory (§4) organizes the **remaining ~17 build efforts** into waves. The
user's cadence is **one item at a time, maker≠checker + `research-skeptic` red-team on
every new gate, one commit per item.** Key dedups already found: **V3 ≡ S2** (one vintage
extension), **V6+V7** share a core (done), **V2** is the substrate for W3/W6, **V5** for W5.

**Option A — Wave 2 (continue the long-tail verifier).** Small gates, mostly extensions:
- **V3+S2** — extend `leakage/vintage.py`: a pretrained/LLM-feature artifact with a
  missing or post-eval training cutoff → `validation_pending`/tracked-debt, not a silent
  pass. (One build, not two.)
- **W4** — extend the ledger: register a search-space cardinality so a one-shot/
  differentiable search feeds DSR its true trial count (anti-conservative-DSR class).
- **S12** — MinTRL (min-track-record-length) + Sortino, beside `metric_plausibility`.
- **V4** — effect-size gate (economic magnitude beside every significance verdict).
- **S4** — promote the private `_persistence_skill` to a public **rejecting** rung-0
  cascade stage, applied to the returns regime (auto-reject if it can't beat persistence).
- **V1** — window-completeness assertion (anti-drop-last) beside `split_integrity`.
- **V8** — spectral-entropy forecastability proxy (feeds confidence/abstention wording).
- **S1** — `frozen_at` + strictly-post-timestamp forward tracking. **Load-bearing MVP
  foundation** — the one contamination gap no after-the-fact detector can close.

Then **Wave 3** (W1 known-positive control, W2 split-key provenance, W3 cheap-heuristic
null [uses V2], W5 stratified noise [uses V5], W6 capacity-matched clause, S18
procedure-audit half) and **Wave 4** (DEBT-statefulness-isolation — the one large item,
flips the 2 xfails; DEBT-S5-contemporaneous red-team).

**Option B — edge discovery (providers → cached MVP screen).** The verifier is now strong
enough to *trust when it says no*. Build read-only **Tiingo + FRED** into a point-in-time,
**delisting-aware** cache (API keys are human-supplied env vars — stop and ask how they're
provided; **no secrets in the repo**), then the **cached MVP screen** (H1–H3 seeds;
batch-6 evidence favors **leading with H3/volatility**), run calibration-first, every trial
through the ledger, every promotion through the cascade + hooks + `research-validator`,
every survivor red-teamed. Robinhood stays read-only-data-only, itself a later gate.

**Recommendation:** either is defensible. Wave 2's **S1** and Option B's providers are the
two highest-leverage next steps (both feed the eventual MVP). If the goal is to reach a
*validated survivor* fastest (the edge-first destination), lean **Option B**, building only
the Wave-2 items the MVP actually needs (S1, S4, V1) alongside it.

**What NOT to do:** begin providers/execution or ML/forecasting without recorded go-ahead;
wire a review check as a hard-rejecting cascade stage; run a gross-of-cost or
non-delisting-aware backtest; let the assistant execute / hold credentials; exceed the
phase authorized in `STATE.md`. If a step would begin a new phase, touch credentials, or
widen autonomy, **stop and ask.**

## 9. Open decisions for the user

- **Wave 2** (finish the long-tail verifier) or **edge discovery** (providers → MVP) next?
  Or a hybrid (providers + only S1/S4/V1)?
- If edge discovery: confirm go-ahead for **read-only Tiingo/FRED adapters** — and how are
  the API keys supplied at runtime (which env var names)?
- Lead the MVP with **H3/volatility** (best-evidenced) or the full H1–H3 set?
- Any change to the edge-first gate or the phased ladder before either path starts?

## 10. Standing constraints (unchanged, non-negotiable)

Research/validation now; the human operates any future live capital; the assistant never
executes live or holds credentials; autonomy is always bounded / observable / stoppable;
no secrets in the repo; canonical labels in the research layer; maker ≠ checker;
explicit-path git with per-commit/push approval; validation precedes capital; **edge before
infrastructure.**

## 11. Lessons worth carrying (see `tasks/lessons.md` for all)

The load-bearing ones, distilled: **continued adversarial red-teaming pays off even on
committed, green code** — the skeptic found a real fail-open in *every* Wave-1 gate that
unit tests missed; do it for every new gate. **A softer disposition must never mask a
harder one** (reject > validation_pending > needs_human_review), and a review flag must
never short-circuit past a later reject. **Fail closed on the unverifiable** — a hash that
would collide or hash a degenerate/empty input to a constant, a NaN/inf that defeats a
naive `<`/`>` gate, an un-instrumented comparison, a non-bracketing sweep: all must fail
(reject or validation_pending), never pass. **A gate's own knobs and thresholds are attack
surfaces** — validate them (finite, in-range) and treat the tunable ones as
pre-registration-load-bearing. **When you change control flow** (e.g. short-circuit →
continue), audit every property/consumer that assumed the old flow. And above all —
**edge before infrastructure.**
