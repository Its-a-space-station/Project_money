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
- [ ] Package 2 config — staged-pipeline skill + subagent role definitions;
      trajectory-judge prompt + no-unverified-confirmation hook.
- [ ] Package 3 — data-tool registry framework (no live adapters), tool-factory
      validation gate, object-memory/ordering rules doc, gated skill/lessons
      evolution loop config.

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
