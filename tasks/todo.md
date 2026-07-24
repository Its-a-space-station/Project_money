# Todo — Project_money

> Conventions: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked /
> needs decision. Nothing here authorizes leaving the current phase.
> **Session handoff:** see [HANDOFF.md](../HANDOFF.md) for the full session
> summary and the next-steps sequence.

## Active — governance pivot (research-only → research-and-trading)

- [x] **CLAUDE.md rewritten (2026-07-22)** to reflect the corrected project
      intent: validated strategies are executed as automated trades via
      Robinhood, **human-operated**, built through a gated ladder (dry-run →
      paper → shadow-canary → human-approved live → later bounded auto-trade).
      Prime directives preserve the invariants that hold regardless: the
      assistant builds/validates but never itself places a live order, moves
      funds, flips to live, or handles credentials; autonomy stays bounded /
      observable / stoppable / validation-gated. Reference design = the user's
      Kalshi bot guardrails. **Uncommitted; pending user review.**
- [x] **Coordinated doc updates DONE (2026-07-22).** Rewrote/updated to match
      the pivot, keeping every real safety invariant: `docs/safety_policy.md`
      (division-of-labor as the top hard constraint; validation-before-capital;
      bounded/observable/stoppable autonomy; phased ladder),
      `docs/broker_strategy.md` (read-only-first → gated execution ladder +
      guardrail requirements, Kalshi as reference), `STATE.md` (phase, scope,
      approved-decision, safety-rules, non-goals, active-loops),
      `docs/report_policy.md` + `docs/label_policy.md` (execution-layer
      carve-out; research vocabulary + schema enums untouched),
      `docs/loop_architecture.md`, `docs/promotion_policy.md`,
      `docs/architecture.md`, `docs/claude_code_workflow.md`,
      `docs/provider_strategy.md`. Governance layer swept clean of stale
      "research-only/no-execution" assertions (historical batch-synthesis docs
      left as accurate records). Suite: 170 green (no code changed).
      **Uncommitted; pending user review.**
- [!] **Note:** CLAUDE.md sets the destination but records NO authorization to
      begin building execution — each phase starts only on explicit approval
      recorded in STATE.md. The 1–4 ungating decision (below) and any
      execution-phase authorization remain the user's to give.

## Active — information intake (COMPLETE) → ungating RECORDED

- [x] **1–4 ungating RECORDED in STATE.md (2026-07-22, user authorized
      in-session).** All six batches ingested; the user gave explicit in-session
      approval to (1) deterministic MVP on cached data, (2) Tiingo+FRED read-only
      adapters, (3) bounded strategy search, (4) paper-candidate forward tracking.
      Recorded in STATE.md approved-decisions.
- [x] **First research phase authorized (2026-07-22).** Verifier hardening first,
      then read-only providers, then the cached MVP screen (H1–H3, delisting-aware
      panel). See "research phase 1" below.
- [ ] Optional (documentation, no gate needed): transcribe batch-2 coverage gaps
      (trading_corpus_synthesis.md §8) into the research backlog.

## Active — research phase 1: verifier hardening (authorized 2026-07-22)

> Edge-first: make the harness's passes and rejections trustworthy BEFORE trusting
> any strategy screen. Pure research-tooling code — no provider, no execution, no
> secrets. maker ≠ checker throughout; every new detector gets bracket tests
> (clean signal passes, junk fails) AND an adversarial red-team pass; suite stays
> green + deterministic.

- [x] Localize: extracted the exact S1–S30 / V1–V8 / W1–W6 spec + known-bad
      specimen list (V/W items live in §4.1, not §3), and mapped the current
      harness API + extension points. Baseline confirmed: 170 green in ~1.5s.
- [x] **Known-bad specimen fixture set — ALL FIVE §9 specimens closed
      (calibration-first milestone reached).** Mehtab-Sen intra-bar (S6),
      CNN-LSTM shuffled split (S9), MarketSenseAI time-travel (S3), Nabipour
      flat-horizon (S5/S10), Paper 8 compound (scaler-leak via check_no_lookahead
      + S11 impossible-accuracy + S16 cost gate). (Stockformer + DeepFund are §4
      metric-falsification / positive-control exemplars, not in the §9 five.)
      `tests/specimens.py` holds each specimen + its causal counterpart.
- [x] S6 — intra-bar contemporaneous-leakage detector (`leakage/intrabar.py`):
      execute-and-compare, exhaustive positions, wide vol-scaled probes, tight-atol
      sign/NaN change, determinism pre-check, cold-reindex statefulness probe,
      fail-closed. 19 tests (fail-before + 9 red-team regressions). **3 red-team
      rounds converged**: r1 5 holes, r2 3 more (all fixed), r3 all confirmed
      closed. 1 xfail = compute-once-cache isolation limit (verification debt).
- [x] S9 — temporal split-integrity detector (`validation/split_integrity.py`):
      catches CNN-LSTM shuffled split; passes forward + purged walk-forward.
      **3 red-team rounds, robust**: tz/NaT/dup/unsorted `full_index` all
      fail-closed; honest purge/embargo scope + `full_index` gap check. 13 tests.
- [x] S5/S10 — forecast diagnostics (`validation/forecast_diagnostics.py`):
      **3 red-team rounds**. S5 = three-regime persistence-null design
      (integratedness inference; returns R² bar; abstain on overlapping returns) +
      r3 fixes (returns bar raised to 0.5 & framed as review; integratedness
      hysteresis). S10 = distributed-growth + fail-closed on non-finite (robust).
      19 tests. Lesson recorded (gate-against-the-null).
- [x] S11/S16 (Paper 8) — `validation/metric_plausibility.py`: impossible-accuracy
      alarm (S11) + cost gate (S16). Closes the Paper 8 compound specimen with the
      scaler-leak (check_no_lookahead). **Red-team round 1 found real logic defects
      (S16 NaN fail-OPEN; trusted reported scalars; net==gross accepted; S11 crash
      on non-float) → all fixed** (math.isfinite fail-closed; artifact recompute;
      net≥gross rejection; drop the FP-prone rate floor). 13 tests green. Lessons
      recorded (NaN fail-open + sibling fail-direction; recompute-don't-trust;
      one-sided alarms must be composed).
- [ ] **Verification debt (tracked, not silent):** (a) `max_test_bars` fast path
      is a best-effort screen — subsample data-derived but recomputable; exhaustive
      (default) is trustworthy. (b) Fully adversarial *stateful* signal_fns need
      process isolation (cold-reindex probe closes the index-keyed case only) —
      applies to `check_no_lookahead` too. (c) S5 abstain regime is a
      metric-honesty gap for φ<0.97 autocorrelated-stationary repackaged-persistence
      (not capital-at-risk; backstopped by the honest-null requirement +
      forward-tracking). (d) S5 delegates contemporaneous leaks to the one-bar
      execution lag + S6 + walk-forward — **TODO: dedicated red-team confirming
      those cover autocorrelated/level targets** (skeptic-recommended). (e)
      **Review-disposition checks** (S11, S5 returns bar, S10, S16 rate-advisory)
      are `needs_human_review`, not auto-reject — but `CheckResult` is binary and
      `run_cascade` maps any fail→reject. When wiring these into the cascade, give
      them a machine-readable review disposition (do NOT register them as rejecting
      stages). (f) S11/S16 are one-sided alarms — compose with edge-existence gates
      (deflated Sharpe, no-lookahead), never trust alone. (g) S18 universe/
      survivorship point-in-time audit is Paper 8's remaining (un-built) channel.
- [x] S3 — MarketSenseAI time-travel: confirmed the existing vintage auditor
      labels a post-cutoff model contaminated; locked with a named regression
      test. (S2 feature-level extension noted as a small future add.)
- [x] S7/S8 — non-causal transform leakage via `check_causal_transform`
      (`validation/invariants.py`): generalizes `check_no_lookahead` to any
      preprocessing/feature transform via one shared whole-window causality core.
      Catches full-sample scaling (S8), detrend/decomposition (S7), bidirectional
      smoothing (S8); passes causal counterparts. **Red-team found a CRITICAL flaw
      in the SHARED CORE (and thus the committed check_no_lookahead): whole-window
      truncation only tests the boundary row, so finite-horizon (1-day) lookahead
      dodged onto the evenly-spaced grid + the tail was untested.** Core rewritten:
      **exhaustive cutoffs** (no grid to game, tail covered), determinism/
      statefulness pre-check (distinct diagnosis), fail-closed coercion + column
      checks, relative tolerance. 15 tests incl. grid-gamed-lookahead + tail-leak +
      stateful + fail-closed regressions; 1 xfail (fit-once needs isolation). Lesson
      recorded. **check_no_lookahead retroactively hardened.**
- [x] S26 — calibration / process-fidelity axis (`validation/calibration.py`):
      `expected_calibration_error` + `reliability_curve` + `check_calibration`
      (review axis, necessary-not-sufficient). Closes the last §6-GAP
      evaluation-axis item. **Red-team round 1 found the fixed 0.1 bar flags a
      PERFECT forecaster ~89% of the time at N=50 (CRITICAL FP) and count-weighted
      ECE forgives a confident-tail (CRITICAL FN) → redesigned:** seeded
      parametric-bootstrap null band (self-calibrating; the documented CI debt made
      load-bearing), a finer-binning pass, and a coverage floor. Lesson recorded.
      **Round 2 confirmed all 4 closed; found residuals (MCE count-floor seam FN,
      multiple-testing FP inflation, degenerate-0/1, coverage-on-predictions) →
      redesigned:** per-bin *studentized* test with a family-wise studentized-max
      null (controls multiplicity; no count floor), conf-clipped noise floor,
      coverage on (pred,outcome) pairs, order-invariant sorted bootstrap. 16 tests
      incl. round-1 + R2-1 regressions. **Both red-team rounds converged.**
      (Compose with prequential_log_loss for proper-scoring blow-ups; sub-finest-bin
      anti-calibration + small-N power loss are inherent, tracked.)
- [ ] S2 — model/embedder training-cutoff vs eval-window contamination (extend vintage to LLM-derived features).
- [ ] S18 — universe/survivorship point-in-time audit (Paper 8's remaining channel); S12 min-track-record-length; S4 mandatory persistence null as a cascade stage.
- [ ] S1 — `frozen_at` + strictly-post-timestamp forward tracking (research-only).
- [ ] V1–V8 (batch-4) + W1–W6 (batch-5) verifier items — sequence after the
      S-items; dedupe overlaps first.
- [x] research-skeptic red-team of every new gate — done for all detectors built
      this phase (S6 ×3, S9/S5/S10 ×3, S11/S16 ×1, S7/S8 + core ×1, S26 ×2);
      still applies to any FUTURE gate.

### Review — verifier-hardening phase (2026-07-22 → 2026-07-23)

**Done & verified.** Research phase 1 (edge-first verifier hardening) delivered the
leakage/plausibility/calibration detection layer, all red-teamed to convergence and
committed in six commits (`e6bf78b`→`8339581`, `main`, unpushed). Suite: **263
passed, 2 xfailed, deterministic** (170 baseline preserved + 93 new).

- **All five §9 known-bad specimens are provably rejected** (Mehtab-Sen intra-bar
  S6, CNN-LSTM shuffle S9, Nabipour flat-horizon S5/S10, MarketSenseAI S3, Paper 8
  compound S11/S16+scaler). **All four §6-GAP items built** (S6 intra-bar, S7/S8
  non-causal transforms, S26 calibration axis).
- **The red-team was load-bearing, not ceremony:** ~30 real holes found & fixed,
  incl. two CRITICAL ones in *already-committed* code — the `check_no_lookahead`
  grid-gaming/untested-tail flaw (exhaustive cutoffs) and the S26
  perfect-forecaster false-positive (bootstrap null band). Unit tests missed both.
- **9 durable lessons** recorded (execute-and-compare purity precondition;
  finite-horizon leaks need exhaustive cutoffs; verifier knobs are attack surfaces;
  gate-against-the-null; NaN fail-open + sibling fail-direction; recompute-don't-
  trust; one-sided alarms must be composed; binary pass/fail conflates
  reject-vs-review; bootstrap-null band for finite-sample-biased gate metrics).
- **Verification debt tracked** (7 items): `max_test_bars` best-effort;
  adversarial-statefulness needs isolation (2 xfails); S5 abstain-regime honesty
  gap + contemporaneous-leak delegation; review-disposition cascade wiring; S18
  survivorship un-built; S26 sub-finest-bin / small-N inherent limits.

**Deferred to next phase (each gated, none started):** provider adapters
(Tiingo/FRED read-only → point-in-time cache) → cached MVP screen (H1–H3,
delisting-aware) — the edge-discovery run; plus the long-tail verifier items below
(S1/S2/S18, V/W dedup) as the MVP needs them. Beginning provider adapters is a new
build step requiring explicit go-ahead per CLAUDE.md §6.

## Active — research phase 1 (cont.): long-tail verifier items

> A read-only dedup **inventory** (workflow `wf_eeae6712-d2a`) mapped the 23
> remaining verifier items (V1–V8, W1–W6, S1/S2/S4/S12/S18, 4 debt items) against
> the harness with file:line evidence. Headline: most V/W items are `partial`
> (substrate exists, gate doesn't) — the dedup **merges** work, it does not
> eliminate it. Net ≈17 build efforts, 1 skip, 1 half-blocked-on-data. Key dedups:
> **V3 ≡ S2** (one vintage extension), **V6+V7** share a ranking-stability core,
> **V2** is the shared substrate for W3/W6, **V5** for W5, **DEBT-statefulness**
> fixes S6 + the shared causal core in one change. **DEBT-max-test-bars = SKIP**
> (safe default already exhaustive; guard by policy, not code). **S18**
> membership-half is blocked on the (gated) provider panel. User chose (2026-07-23):
> **foundational item only, then re-plan.**

### DEBT-review-disposition — machine-readable needs_human_review vs reject (IN PROGRESS)

> Highest-stakes debt item. `CheckResult`/`StageResult` were binary and
> `run_cascade` mapped ANY fail → `reject`; wiring S11 / the S5 returns-bar / S10 /
> S26 (documented `needs_human_review`) as stages would hard-reject legitimate
> strategies. Currently latent (no real check is wired into a cascade yet) — fix the
> plumbing BEFORE anything is wired. maker≠checker + skeptic red-team.

- [x] `CheckResult` gains a `disposition` field (`reject` default | `needs_human_review`),
      validated (`__post_init__`), **frozen** (matches `Stage`; blocks post-hoc softening);
      shared disposition constants (`REJECT`/`NEEDS_HUMAN_REVIEW`/`FAILURE_DISPOSITIONS`) in
      `invariants.py`, exported from the package.
- [x] Cascade tri-state: `StageResult.disposition`; `run_cascade` precedence where a review
      flag NEVER short-circuits (so a later hard reject / exception still wins) while reject
      & exception do; new label `needs_human_review`; `Stage.from_check` adapter; unknown
      disposition + malformed shape fail-closed (reject / validation_pending); empty-cascade
      → validation_pending (was fail-open to trigger_ready); `failed_stage` disposition-aware
      (names the rejecter, not an earlier review); `review_stages` property.
- [x] Set the correct disposition on the review checks (S11 implausible-accuracy; S5
      returns-bar with most-severe-wins vs the R²>0.99 / persistence hard reasons; S10;
      S26) — NOT registered as live cascade stages (debt item e respected).
- [x] Tests: 33 in `tests/test_review_disposition.py` (precedence, from_check end-to-end,
      per-check disposition, CheckResult validation/frozen, + 5 skeptic-round-1 regressions).
      Suite **296 passed, 2 xfailed, deterministic** (263 baseline preserved).
- [x] research-skeptic red-team + independent code review — round 1 confirmed the **safety
      invariant holds** (review never masks reject/validation_pending; reject never softened;
      unknown→reject; S5 most-severe-wins verified numerically). Skeptic found 4 real defects
      (failed_stage provenance, empty-cascade fail-open, reason pollution, unfrozen
      CheckResult) — ALL FIXED + regression-tested. **Round-2 re-verify: GO** — all 4 fixes
      sound, no new holes; found 1 residual (empty *generator* still promoted — truthiness
      guard) → hardened (`stages = list(stages)`, total empty-guard) + tested. Suite **297
      passed, 2 xfailed, deterministic**.
- [x] **S10 disposition split (skeptic #5) — RESOLVED (user-approved my call 2026-07-23).**
      A strictly *inverted* (decreasing) horizon-error curve now hard-`reject`s (matching S5's
      level-lag leakage fingerprint); a merely flat/uneven-growth curve stays
      `needs_human_review` (possibly an unpredictable series). Most-severe-wins, mirroring S5.
      Phase-1 S10 regressions still green.

### Review — DEBT-review-disposition (2026-07-23)

**Done & verified (uncommitted).** The cascade can now emit a machine-readable
`needs_human_review` — the highest-stakes long-tail item, built foundational-first at
the user's direction. Files: `validation/{invariants,cascade,metric_plausibility,
forecast_diagnostics,calibration,__init__}.py` + new `tests/test_review_disposition.py`
(34 tests). Suite **297 passed, 2 xfailed, deterministic** (263 baseline preserved).

- **Safety property proven by two independent adversaries** (research-skeptic +
  code-reviewer): a `needs_human_review` can never mask a `reject`/`validation_pending`,
  and a genuine `reject` is never softened. Mechanism: a review flag does NOT short-circuit
  (so a later hard reject/exception still wins), reject & exception do, unknown dispositions
  fail-closed to reject, `CheckResult` is frozen.
- **The red-team was load-bearing again** (phase-1 meta-lesson reconfirmed): unit tests were
  green, yet the skeptic found 4 real defects — incl. a `failed_stage` provenance regression
  *I introduced* by changing short-circuit→continue, and a pre-existing empty-cascade
  fail-open (no-op promoted). All fixed; a round-2 re-verify found + closed a further residual
  (empty-generator fail-open). Every fix has a regression test.
- **Scope held:** the review checks emit the right disposition but are NOT registered as live
  cascade stages (debt-e respected). The one flagged semantic decision (S10 inverted-curve →
  reject) was surfaced and, with user approval, resolved (split; see above).

**Deferred (for the re-plan):** the remaining ~16 long-tail items (V/W/S +
statefulness-isolation + S5-contemporaneous red-team) per the `wf_eeae6712-d2a` inventory —
**next: Wave 1 shared substrates (V2 / V5 / V6+V7 core), user-approved.** No
providers/execution/secrets touched.

## Bootstrap (done)

- [x] Convert original brief `.rtf` → `CLAUDE.md`.
- [x] Adopt the playbook: core `docs/`, `schemas/`, `templates/`, `checklists/`.
- [x] Merge quant-research philosophy + playbook operating rules in `CLAUDE.md`.
- [x] Set schema `project` enum → `project_money`; extend `object_type`.
- [x] Write `STATE.md`, `tasks/`, `README.md`, `AGENTS.md`, blueprint, `.gitignore`.
- [x] Verify docs are internally consistent (cross-links resolve; canonical labels).

## Tooling pre-phase (authorized 2026-07-20): papers synthesis → tool proposals

- [x] Deep-read the 38-paper corpus in "~/Documents/Papers on Coding/" via six
      parallel thematic agents (mechanism-level, tool-design mandate).
- [x] Cross-check agent digests against the playbook's
      `reference_papers_coding_agents.md` — independent verification: **no
      contradictions; every checkable headline confirmed** (see synthesis §2).
- [x] Write [docs/agent_tooling_synthesis.md](../docs/agent_tooling_synthesis.md):
      verdict, 10 design principles, 11 proposed tools in 3 packages,
      finance-specific cautions, cluster digests, provenance map.
- [x] Present ranked, paper-backed tool proposals for user selection — user
      selected **all three packages** and lifted the scope guard for
      research-tooling code (providers/brokers/execution remain gated).

## Tool build (authorized 2026-07-20; synthesis §4 is the spec)

- [x] Package 1 — verification backbone (code + tests): invariants (incl.
      whole-window lookahead check), metrics + deflated Sharpe, walk-forward
      (purge/embargo), prequential codelength, cascade runner, vintage/leakage
      auditor, known-zero controls + falsification harness. **81 tests, all
      green, deterministic across runs.**
- [x] Package 2 core code — hypothesis ledger (append-only JSONL trial
      registry, tabu memory, canonical-status enforcement, expected-max-null-
      Sharpe bar) + MDL gate (knob hurdle, permuted-null COMP, noisy-knob
      jitter). Tested in the same suite.
- [x] Package 2 config: `.claude/agents/` (data-navigator, strategy-analyst,
      research-validator, research-skeptic), `.claude/skills/research-pipeline`,
      `.claude/skills/trajectory-judge`, finding-promotion hooks
      (`hooks/validate_finding.py` + `hooks/guard_findings_bash.py` +
      `.claude/settings.json` + `findings/`).
- [x] Package 3: `src/project_money/registry` (typed read-only tool registry,
      two-tier docs, ranked search), `src/project_money/toolfactory` (held-out
      admission gate incl. lookahead hook), `src/project_money/memory`
      (stable ids, canonical sort, order-invariant digest),
      `docs/object_memory_and_ordering.md`, `docs/skill_evolution_policy.md`.
- [x] Adversarial review of the config layer (4 lenses × 2-skeptic
      verification, 82 agents): 32 confirmed findings — ALL fixed with
      regression tests; 7 refuted.
- [x] Post-review: the Bash findings-guard false-positived on `git commit`
      (keyword co-occurrence); rewritten target-aware. Suite: **163 tests
      green, deterministic.** Committed + pushed (`803be80`).

## Review — config layer (2026-07-20)

The adversarial workflow confirmed real defects the unit tests missed, all
now fixed + regression-tested: the promotion hook failed OPEN on exceptions,
relative/case-variant paths, Bash writes, missing `maker`, any-file
"artifacts", and `*README.md` suffixes (now: fail-closed wrapper, normalized
root-anchored paths, Bash guard hook, maker required, artifacts must be JSON
under `outputs/`, exact README exemption); `canonical_sort` ordered numbers
as JSON strings; a constraint-free admission case passed a known-wrong tool;
default-omission dodged the held-out check; bool matched int in known-answer
tests; array outputs crashed the gate; the registry's forbidden-token screen
missed entry/exit/recommendation and param names; the pipeline skill leaked
promotion thresholds to the maker (firewall restored); data-navigator had
Bash despite a read-only mandate (removed). Deferred by design: the
TOOLMAKER-style build harness (admission gate only for now, next bullet).

## Information intake (batch 2 — trading-books corpus: COMPLETE)

- [x] Six thematic agents read the 28-book corpus (~1,100 of ~9,000 pages,
      TOC-first strategic sampling). Two agents were API-interrupted and
      resumed from transcript; all six delivered complete digests.
- [x] Synthesized into
      [docs/trading_corpus_synthesis.md](../docs/trading_corpus_synthesis.md):
      evidence-tiered source map (T1–T4), nine-mechanism bank, 25
      consolidated hypothesis families in three tiers, documented nulls,
      process-doctrine translation, cross-corpus integration.
- [x] Ungating re-rank check: the batch **sharpens but does not reorder**
      the agreed 1–4 plan (MVP seed = Tier-1 families H1–H3; search loop
      seeds = Tier 2; falsification calibration = Tier 3 + nulls). Two data
      implications recorded: delisting-aware equity panel requirement; CFTC
      COT as a future provider candidate. Ungating still **recorded only
      when the user says the information set is complete.**

### Review — batch 2 (2026-07-21)

28 books yielded 1 clean dataset (Blackstar), 1 census (Bulkowski,
conditionals only), 1 evidence broker (K&D), 2 methodology-bearing quant
books (Chan, Fitschen), and ~20 folklore sources whose value is mechanisms +
exactly-specified rules + convergence patterns. Best cross-cluster finds:
the throwback/adverse-drift convergence (Bulkowski × Fitschen), the
five-author pullback skeleton, Chan's VIX sign-asymmetry, and the corpus's
own falsifications (divergence signals, release-direction, measure rules).
All claims enter as `proposed`/`validation_pending`; nothing is promoted.

## Information intake (batch 3 — AI/ML shelf: COMPLETE)

- [x] Four verify-and-extract agents completed over the already-mapped
      20-PDF shelf. Map substantially verified; five citation defects caught
      (minTRL not-in-book; Powell printed-vs-PDF labeling; optimizer's-curse
      depth; Mohri/DasGupta offsets) and — decisively — **three defects in
      our own stack**.
- [x] Wrote [docs/ml_shelf_integration.md](../docs/ml_shelf_integration.md):
      verification results, corrections, consolidated 13-item build list,
      doctrine crosswalk, subsequent-uploads prerequisites.
- [x] **Corrections applied with regression tests** (170 green,
      deterministic): `deflated_sharpe` now takes the ledger's cross-trial
      Sharpes (empirical-variance benchmark per the source; IID-null
      fallback documented), raw-kurtosis validation with corrective hint,
      `kurtosis_raw` metric key, `HypothesisLedger.recorded_sharpes()`
      wiring, trajectory-judge hardening (identity pinning, bias battery,
      n≈20 authority statement).

### Review — batch 3 (2026-07-21)

The verify-and-extract design paid off twice over: the prior map held up
(no content contradictions — its second successful independent audit), and
the pass caught a real anti-conservative defect in our promotion gate that
unit tests could not have found (the formula matched our own tests; it
mismatched the source). Follow-on build items (PSR, ROPE gate, corrected
permutation estimator, fold-split ranking, calibration harness, CPCV/PBO,
conformal, CUSUM monitors) are catalogued in the integration doc §3 —
sequenced for when validation work resumes, not blocking the gates.

## Information intake (batch 4 — time-series forecasting papers: COMPLETE)

- [x] Five verify-and-extract agents over exclusive clusters of the 26-PDF
      corpus (`~/Documents/Papers on Time Series Forecasting/`): LTSF
      transformers; linear/MLP critique; foundation/LLM/scaling;
      representation/graph/exogenous; benchmarking/meta (incl. AIRS-Bench).
      Pattern chosen because the corpus underlies the playbook's **unadopted**
      v2.1 forecasting layer (six policy docs) — audit before any reliance.
- [x] Wrote [docs/ts_forecasting_integration.md](../docs/ts_forecasting_integration.md):
      layer survives its source audit (third successful independent playbook
      audit) with 1 hard defect (Time-LLM listed as probabilistic source;
      point-only), 1 cross-doc inconsistency (ARIMA-vs-DLinear null order),
      9 wording/taxonomy + 4 attribution corrections — recorded as adoption
      prerequisites; 8 verifier build items (V1–V8) + fleet-ops updates +
      pre-specified (gated) forecasting protocol.
- [x] **Maker≠checker on the synthesis itself**: independent checker
      spot-checked 10 headline claims against the PDFs — 8 confirmed, 2
      corrected (a digest had mixed MSE/MAE columns on Zeng Exchange-720 and
      inverted one comparison). Doc fixed; load-bearing figures now
      checker-verified only; lesson added to `tasks/lessons.md`.
- [x] Ungating re-rank check: **sharpens, does not reorder** the agreed
      (unrecorded) 1–4 plan; strengthens the case that ML/forecasting stays
      deferred (baselines first — now externally evidenced). Recording still
      waits on the user's end-of-information signal.

### Review — batch 4 (2026-07-21)

The verify-and-extract pattern paid off for a second consecutive batch, this
time in both directions: the playbook's forecasting layer held (no fabricated
numbers across ~60 claims; one hard defect + taxonomy/attribution
corrections queued as adoption prerequisites), and the checker pass caught a
numeric-extraction defect in **our own fleet's digest** before it hardened
into a flagship exhibit. Best finds: the corpus is a live demonstration of
baselines-as-nulls (Informer/Autoformer's SOTA collapsing to DLinear;
drop-last quantified at ~17%; TFB's NASDAQ row where VAR beats every deep
SOTA); the D-NOW verifier queue (V1–V8) extends the backbone independently
of any forecasting decision; and the foundation-model contamination audit
gives us per-model vintage checks to demand before any zero-shot number is
ever cited. Suite: 170 tests green after all edits. Not yet committed —
awaiting user approval.

## Information intake (batch 5 — graph-ML corpus: COMPLETE)

- [x] Five fresh-read agents over exclusive clusters of the 25-PDF corpus
      (`~/Documents/PWC_graph_ML/`): foundations/architectures;
      evaluation/robustness; interpretability/symbolic;
      GNN-time-series/physics; tooling/scale. Fresh-read pattern chosen
      after confirming zero overlap with playbook/prior batches.
- [x] Wrote [docs/graph_ml_synthesis.md](../docs/graph_ml_synthesis.md):
      verdict "refines rather than expands" — no capability case for graph
      ML on our panels; W1–W6 verifier queue (known-positive controls,
      split-key provenance, cheap-heuristic nulls, full-search-space DSR
      accounting, stratified noise probes, capacity matching); eight policy
      clauses; gated-future pre-specs (graph-null ablation ladder with
      ≤7-param typed-propagation null; distill-then-validate symbolic
      pipeline; Frame-vs-GBDT spec; assignment-with-dustbin entity
      resolution); 14-entry do-not-build ledger.
- [x] Batch-4 MTGNN verdict adversarially re-tested: **confirmed** (GNN4TS
      Table 2 classifies MTGNN as no-prior learned adjacency), reinforced
      from two new directions (VGAE multiplicity; learned-graphs-only-win-
      where-priors-exist), **boundary-corrected** (masked attention is O(d),
      not O(N²) — condemned by SNR economics via the ablation ladder, not
      by the multiplicity argument).
- [x] **Maker≠checker on the synthesis**: independent checker verified 10
      load-bearing claims — 8 confirmed, 2 confirmed-with-correction
      (LinkFeat Hits@10-vs-MRR mislabel; GraphGPT variant merge), 0 refuted;
      5 secondary misstatements corrected in place. Checker also caught the
      maker pre-labeling evidence "checker-verified" before the check ran —
      corrected; lesson added to `tasks/lessons.md`.
- [x] Ungating re-rank check: **sharpens, does not reorder** the agreed
      (unrecorded) 1–4 plan; third domain of nulls-win evidence behind the
      ML deferral. Recording still waits on the user's end-of-information
      signal.

### Review — batch 5 (2026-07-21)

The fresh-read fleet + checker pattern held for a third consecutive batch.
The corpus produced no reason to build graph ML now and several reasons not
to — while contributing the strongest new pipeline idea since batch 3
(Cranmer's distill-then-validate: the symbolic form extracted from a
network beat the network itself out-of-distribution) and a six-item
verifier queue whose best entries (known-positive controls, split-key
provenance, cheap-heuristic nulls) fill genuine false-negative and
plumbing gaps the V1–V8 queue lacked. Checker score improved batch-over-
batch (batch 4: 8/10 with 2 refuted; batch 5: 10/10 with 2 corrected),
but it caught a new process defect — verification-status pre-labeling —
now encoded as a lesson. Suite: 170 tests green after all edits. Not yet
committed — awaiting user approval.

## Information intake (batch 6 — stock-market ML/AI corpus: COMPLETE — FINAL BATCH)

- [x] Eight adversarial-triage agents over exclusive clusters of the 73-file
      corpus (`~/Documents/PWC_stock_market_papers/`), run as a **resumable
      Workflow** (`wf_f7d99529-662`, 16 agents, 0 errors) after two prior
      Fable-model attempts died mid-run on spend/credit limits. Direct-domain,
      highest-junk-density corpus.
- [x] Wrote [docs/stock_market_synthesis.md](../docs/stock_market_synthesis.md):
      **73 papers → CREDIBLE 10 · PARTIAL 23 · JUNK 33 · OTHER 7**; verdict:
      **zero validated tradeable daily-horizon edges** — strongest possible
      in-domain confirmation of the whole doctrine. 10 "credible" papers are
      credible as methods/exemplars, none as an edge. Yield: **S1–S30 verifier
      additions** (contamination/vintage, nulls/metrics, six new leakage-
      detector GAPS incl. intra-bar leakage + calibration axis, cost/universe,
      new evaluation axes), a **dataset catalog** (vintage-tagged), and search
      discipline for the future bounded search.
- [x] **Maker≠checker built into the pipeline**: each cluster's load-bearing
      claims independently verified against the PDFs — **57 checked → 52
      CONFIRMED, 5 CONFIRMED-with-correction, 0 REFUTED** (cleanest of any
      batch). One proposed detector (pretrained-vs-scratch MSE-gap alarm)
      **rejected on verification** and recorded as not-adopted; lesson added.
      Plus a final independent check on the synthesis doc's headline figures.
- [x] Ungating re-rank check: the corpus **reinforces** the agreed 1–4 plan
      and equips its first build step (S1 forward-tracking is the research-only
      analogue of the live benchmarks; S1–S30 are the harness the MVP needs).

### Review — batch 6 (2026-07-22)

The final and richest batch. Because it is our direct domain, its junk exposed
in-domain failure modes — the highest-yield methodological haul of the intake
(S1–S30, six of them GAPS our harness could not previously catch). The single
most valuable specimen is Mehtab-Sen Case III: 94.76% "OOS" accuracy from
intra-bar OHLC leakage that a bar-granularity detector would pass. The flagship
positive result is a negative: Stockformer's own LightGBM null wins the uptrend
backtest net of costs while showing negative IC. DeepFund (NeurIPS) is the
definitive contamination case (8/9 LLMs lose live). The resumable-Workflow
approach recovered what two Fable attempts lost to spend limits. Suite: 170
tests green (no code changed). Not yet committed — awaiting user approval, and
separately awaiting the user's ungating decision (synthesis §11).

## Future (gated — not authorized by this list)

- [!] TOOLMAKER-style tool *build* harness (checkpointed sandbox build with
      diagnose→reimplement→summarise memory) — deferred; only the admission
      gate exists (`src/project_money/toolfactory`). Requires authorization.

## Deterministic MVP (deferred — needs authorization to start)

- [!] Define deterministic, reproducible criteria for one `object_type` (e.g. `equity`)
      on **cached** data.
- [ ] Maker step produces candidates; checker step verifies independently.
- [ ] Assign canonical labels only: `reject`, `watchlist`,
      `trigger_ready_research_candidate`, `needs_human_review`, `paper_candidate`,
      `research_only`, `validation_pending`.
- [ ] Cached-data validator first (guard against lookahead / bad adjustments).

## Reports (deferred)

- [ ] Daily report from `templates/daily_report.template.md` (research-only footer).
- [ ] Weekly report from `templates/weekly_report.template.md`.

## Manual review & calibration (deferred)

- [ ] Route `needs_human_review` / conflicting items via `templates/manual_review.template.md`.
- [ ] Track outcomes; write postmortems for resolved theses; propose config
      changes (proposals require human approval).

## Future integrations (gated — not authorized by this list)

- [!] Tiingo / FRED read-only provider adapters (respect terms & rate limits).
- [!] Robinhood read-only data — gated, no execution path; see
      [docs/broker_strategy.md](../docs/broker_strategy.md).
- [!] Consider adopting playbook v2.1 forecasting layer if/when ML forecasting is authorized.

## Review — 2026-07-20 (playbook adoption)

**Done & verified.** Project_money adopted the Decision Systems Playbook via a
tailored bootstrap, with the quant-research philosophy merged into `CLAUDE.md`.
Verification performed this session:

- Repo-wide relative-link scan → **no broken links** (v2 sections that linked to
  uncopied docs were trimmed; sections renumbered).
- All 6 JSON schemas parse; `project` enum = `project_money`; `object_type`
  extended to `equity/etf/option/macro_signal/factor`.
- Secret scan → none. Action words appear only in safety negations / forbidden
  examples (no action-word labels or field names).
- Merge completeness → every section of the original brief is present in `CLAUDE.md`.
- Repo is non-git → nothing staged or committed.

**Status of remaining boxes: intentionally deferred, not incomplete.** Every
unchecked `[ ]` / `[!]` item above (deterministic MVP, reports, manual review,
calibration, provider/broker adapters) is **gated behind explicit user
authorization to leave the bootstrap phase**, per the scope guards in
[../CLAUDE.md](../CLAUDE.md) §7 and [../docs/promotion_policy.md](../docs/promotion_policy.md).
They must not be started without that go-ahead.

**Follow-ups resolved (user-approved):**

- [x] Deleted the redundant `CLAUDE.md.rtf` (content fully absorbed into `CLAUDE.md`).
- [x] Localized all sibling-system references (eBay / Minervini / Polymarket /
      Kalshi / IBKR) to Project_money across `docs/architecture.md`,
      `docs/label_policy.md`, `docs/safety_policy.md`, `docs/broker_strategy.md`,
      and the broker checklist / todo template. Repo-wide scan → none remain;
      links still resolve.
