# Todo — Project_money

> Conventions: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked /
> needs decision. Nothing here authorizes leaving the current phase.

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
