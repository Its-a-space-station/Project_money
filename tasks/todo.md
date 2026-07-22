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

## Active — information intake (COMPLETE)

- [ ] **END-OF-INFORMATION SIGNAL RECEIVED (2026-07-22).** All six batches
      ingested. **Decision point for the user: record the agreed 1–4
      ungating in STATE.md's approved-decisions ledger** (deterministic MVP
      on cached data → Tiingo+FRED read-only adapters → bounded strategy
      search → paper-candidate forward tracking). Proposed in
      `docs/stock_market_synthesis.md` §11; **NOT recorded — awaits explicit
      in-session user approval** (prior-session agreement ≠ current consent;
      lifting scope guards is a governance action). On approval: record the
      decisions, finalize the MVP spec (H1–H3, delisting-aware panel), and
      build the S1–S30 verifier additions first (the MVP's credibility rests
      on the harness rejecting batch-6's known-bad specimens).
- [!] On the user's **end-of-information signal**: record the agreed 1–4
      ungating in STATE.md, finalize the MVP spec (H1–H3 seeds,
      delisting-aware panel), begin calibration-first execution
      (HANDOFF.md §3.2).
- [ ] Optional while waiting (documentation, no gate needed; user go-ahead):
      pre-draft MVP task specs + checker-owned cascade threshold config;
      transcribe batch-2 coverage gaps (trading_corpus_synthesis.md §8).

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
