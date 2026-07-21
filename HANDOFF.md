# HANDOFF.md — Project_money session handoff

> **Purpose:** a self-contained summary of what was accomplished in the
> 2026-07-20 → 2026-07-21 working session and exactly where things stand, so
> any future session (or the user) can resume without re-deriving context.
> Read alongside [STATE.md](STATE.md) (live snapshot) and
> [tasks/todo.md](tasks/todo.md) (open work). Research-only throughout: this
> system informs a human and never takes financial action.
>
> **Status at handoff:** information intake is ONGOING — the user is still
> uploading material. The agreed capability ungating is intentionally
> unrecorded until the user signals the information set is complete.

---

## 1. What was accomplished, in order

### 1.1 Bootstrap (commit `aa5039e`)

- Converted the original `.rtf` research brief into `CLAUDE.md`, then adopted
  the **Decision Systems Playbook** (`~/Projects/decision_systems_playbook`)
  via its own *tailored bootstrap*: 12 core governance docs, 6 canonical JSON
  schemas (`project = project_money`; multi-asset `object_type`), lean
  templates + checklists, and a project blueprint.
- **Merged** the quant-research philosophy into `CLAUDE.md` as Part II
  (domain layer) under Part I (governance layer); governance wins conflicts.
- Localized all inherited docs to Project_money (no sibling-system references
  remain); **Robinhood scoped as a read-only, gated broker** — no execution
  path, per `docs/broker_strategy.md`.
- Git initialized; first push to
  `https://github.com/Its-a-space-station/Project_money`.

### 1.2 Information batch 1 — coding-agents papers → tooling roadmap

- Six parallel agents deep-read the 38-paper corpus in
  `~/Documents/Papers on Coding/` (mechanism-level, tool-design mandate),
  deliberately unanchored to the playbook's prior map — which they then
  independently **confirmed with zero contradictions**.
- Output: [docs/agent_tooling_synthesis.md](docs/agent_tooling_synthesis.md)
  — verdict ("the verifier is the product; loops find the verifier's defects
  before they find truth"), 10 design principles, **11 proposed tools in 3
  packages**, finance-specific cautions (backtests are noisy verifiers —
  gaming is *easier* than in code/math).

### 1.3 Tool build — all three packages (commits `e32a967`, `803be80`)

User decisions recorded in STATE: build all three packages; **scope guard
partially lifted — research-tooling code authorized** (providers/brokers/
execution still gated).

Built and tested (`src/project_money/`, `tests/`, `.claude/`, `hooks/`):

- **Verification backbone**: stage-0 invariants incl. a whole-window
  **lookahead detector**; multi-metric evaluation recomputed from artifacts;
  **deflated Sharpe** (multiplicity-corrected); walk-forward with
  purge/embargo; prequential codelength vs null; staged **evaluation
  cascade** emitting canonical labels only.
- **Leakage/vintage auditor** (data vintage vs knowledge cutoff vs
  formation date; point-in-time exemption).
- **Falsification harness**: known-zero controls (permutation, block
  permutation, surrogates), bracket tests, nuisance sweeps, differential
  validation.
- **Hypothesis ledger**: append-only JSONL trial registry (feeds DSR), tabu
  memory, repeat-failure freeze counts, canonical-status enforcement.
- **MDL complexity gate**: per-knob bits hurdle, permuted-null capacity
  (COMP), noisy-knob jitter test.
- **Config layer**: four subagent roles (data-navigator, strategy-analyst,
  research-validator, research-skeptic), two skills (research-pipeline with
  generator↔gate firewall; trajectory-judge), **finding-promotion hooks**
  (`hooks/validate_finding.py` + Bash guard, wired in `.claude/settings.json`
  — no promoted label without an executed JSON artifact under `outputs/`,
  maker ≠ checker recorded, fail-closed), typed read-only **tool registry**,
  **tool-factory admission gate**, memory/ordering helpers, and two policy
  docs (`object_memory_and_ordering.md`, `skill_evolution_policy.md`).
- **Adversarial review**: an 82-agent workflow (4 lenses × 2-skeptic
  verification) confirmed **32 real defects — all fixed with regression
  tests** (promotion-hook bypasses, string-sorted numerics, vacuous admission
  cases, firewall leak, least-privilege violations).

### 1.4 Information batch 2 — trading-books corpus (commit `f2166c0`)

- Six agents strategically read the 28-book practitioner corpus
  (`~/Documents/Github books on Trading/`, ~1,100 of ~9,000 pages).
- Output: [docs/trading_corpus_synthesis.md](docs/trading_corpus_synthesis.md)
  — evidence-tiered source map (T1–T4), **nine-mechanism bank** ("who is on
  the other side"), **25 consolidated hypothesis families** in three tiers
  (Tier 1 = MVP seeds; Tier 2 = search-loop population; Tier 3 =
  falsification batteries), documented nulls the corpus itself supplies, and
  process doctrine translated to research-only form.
- Verdict: sharpens but does not reorder the ungating plan. Two data
  implications: the equity panel must be **delisting-aware**; CFTC COT is a
  future provider candidate.

### 1.5 Information batch 3 — AI/ML shelf verify-and-extract (commit `8d499c2`)

- The 20-PDF shelf (`~/Documents/Github book on AI_ML engineering/`) was
  already mapped by the playbook; four agents **verified the map against the
  sources** (second independent audit — held, with five citation defects
  recorded) and extracted implementation-grade specs.
- Output: [docs/ml_shelf_integration.md](docs/ml_shelf_integration.md).
- **Three defects in our own stack found and fixed with regression tests:**
  1. `deflated_sharpe` benchmark was anti-conservative — now uses the
     empirical cross-trial variance (`trial_sharpes`, wired from
     `HypothesisLedger.recorded_sharpes()`); IID-null fallback documented.
  2. Kurtosis-convention hazard — raw-kurtosis validation + `kurtosis_raw`
     metric key.
  3. Trajectory-judge authority overstated — identity pinning, bias battery,
     and an explicit n≈20-labels authority limit added to the skill.

### 1.6 Governance decisions made (and deliberately NOT made)

- **Agreed in principle, NOT yet recorded:** ungating items 1–4 (deterministic
  MVP on cached data; Tiingo+FRED read-only adapters with point-in-time
  cache; bounded evolutionary strategy search; paper-candidate forward
  tracking). Recording waits for the user's **end-of-information signal**.
- **Deferred by decision:** scheduled loops (after adapters prove out), ML/
  forecasting layer (baselines first), tool-build harness, Robinhood
  read-only (revisit after providers mature), options/macro/cross-asset.
- **Closed permanently:** execution paths, scraping/ToS evasion, weakening
  verification discipline.

---

## 2. Current state snapshot

- **Repo:** `https://github.com/Its-a-space-station/Project_money`, branch
  `main`, HEAD = `8d499c2`, working tree clean at handoff (modulo this file
  and the STATE/todo updates accompanying it).
- **Test suite:** `./.venv/bin/python -m pytest` → **170 passed**,
  deterministic across runs. Venv at `.venv/` (Python 3.14, numpy/pandas,
  `pip install -e ".[dev]"`).
- **Hooks are ACTIVE in this repo** (`.claude/settings.json`): all
  Write/Edit-family calls run the finding-promotion validator; all Bash calls
  run the findings-write guard. Both fail closed.
- **Knowledge base** (the three batch syntheses + inherited governance):
  `docs/agent_tooling_synthesis.md`, `docs/trading_corpus_synthesis.md`,
  `docs/ml_shelf_integration.md`, plus the playbook's `reference_library.md`
  (canonical shelf map) and `reference_papers_coding_agents.md`.
- **Startup reading for a fresh session:** `CLAUDE.md` → `STATE.md` →
  `tasks/todo.md` + `tasks/lessons.md` → this file → the three synthesis
  docs as needed.

---

## 3. Next steps

### 3.1 While uploads continue (no gate needed)

1. **Ingest each new information batch** with the established pattern:
   thematic agent fleet → mechanism/evidence extraction → cross-check against
   prior syntheses → repo synthesis doc → STATE/todo update → commit on user
   approval. (Three worked examples in §1.2/1.4/1.5.)
2. Optional documentation work the user may green-light at any time:
   pre-draft the **MVP task specs** (statement/requirements/interface for
   H1–H3) and the **checker-owned cascade threshold config**; transcribe the
   batch-2 coverage gaps listed in `trading_corpus_synthesis.md` §8.

### 3.2 On the user's end-of-information signal

1. **Record the 1–4 ungating** in STATE.md's approved-decisions ledger.
2. Finalize the MVP spec against the complete information set. Seeds:
   Tier-1 families **H1 (momentum), H2 (short-horizon reversal), H3
   (volatility-state conditioning)** on a **delisting-aware daily equity/ETF
   panel**.
3. Execute **calibration-first**: (a) falsification battery proven on
   documented nulls + Tier-3 low-prior claims (the harness must reject known
   junk before its passes mean anything); (b) Tier-1 baselines established
   (they become the null every later hypothesis must beat); (c) Tier-2
   ablations against those baselines. All trials through the ledger; all
   promotions through the cascade + hooks; skeptic red-teams survivors.
4. Build the **follow-on validation items** as needed, in the ranked order of
   `ml_shelf_integration.md` §3 (PSR, ROPE gate, corrected permutation
   estimator, fold-split ranking + shrinkage, calibration harness, then
   CPCV/PBO, conformal, CUSUM monitors, FFD).

### 3.3 Standing constraints (unchanged by anything above)

Research-only; no autonomous financial action; providers/brokers gated
separately (Robinhood strictest); no secrets in the repo; canonical labels
only; maker ≠ checker; explicit-path git with user approval per commit/push.

---

## 4. Session lessons worth carrying forward

Recorded in [tasks/lessons.md](tasks/lessons.md): lookahead detectors compare
whole windows; null-draw test flakiness is selection-on-noise in miniature;
enforcement boundaries are attack surfaces (fail closed, normalize paths,
cover every write route, red-team the gate); **verify implemented formulas
against primary sources before gating on them** (the DSR correction); and the
Robinhood capability-is-not-authorization principle.
