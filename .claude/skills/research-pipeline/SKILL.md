---
name: research-pipeline
description: Run one hypothesis through the staged research pipeline — localize → spec → register → build → validate → select → report. Use whenever a strategy idea is to be investigated end-to-end; enforces maker ≠ checker, ledger registration, and canonical labels throughout.
---

# Research Pipeline — staged, typed, verification-first

Fixed stages with typed hand-offs (Agentless doctrine: staged pipelines beat
free-roaming agents on recurring work). One hypothesis per run. Research-only
throughout: outputs inform a human; nothing here acts.

## Stage 0 — LOCALIZE (subagent: `data-navigator`)

Input: the research question.
Output contract: `{pointers[], coverage, vintages, gaps[]}` — compressed views
only. If a required dataset is missing/stale → stop; report the gap
(env-readiness is the #1 failure class; do not improvise data).

## Stage 1 — SPEC

Write the task spec before any code (the ~3× lever): **statement**
(hypothesis, one sentence: what edge, why it should exist), **requirements**
(universe, date range, horizon, cost assumption, and *which* metrics the
cascade will compute — referenced by cascade-config id only; the exact
promotion thresholds live in the checker-owned config and are **never copied
into the spec**: generator↔gate firewall, SWE-smith's checker-leak result),
**interface** (exact artifact contract: signal function signature, finding
JSON fields, output paths). The spec's failure conditions double as the
cascade's fail-before checks.

## Stage 2 — REGISTER (ledger, before any evaluation)

Append the hypothesis to the ledger (`project_money.ledger.HypothesisLedger`)
with family, params, `status="proposed"`. Check `is_tabu()` and the discarded
history: within tabu distance of a discarded trial → differentiate explicitly
in the entry notes, or abandon now. **Every evaluated variant is a ledger
entry** — untracked trials silently inflate every later Sharpe.

## Stage 3 — BUILD (subagent: `strategy-analyst`, k variants)

The maker implements the spec: causal signal code (self-checked with
`check_no_lookahead`), backtest artifacts via
`project_money.validation.metrics`, finding JSON at `label:
"validation_pending"`. Sample-many where variants are natural (k=2–3), kept
as separate candidates. **Firewall:** the maker works from the spec only — it
never sees held-out windows, the cascade's exact thresholds, or validator
internals (DGM: gate-hacking increases with checker visibility).

## Stage 4 — VALIDATE (subagent: `research-validator`; independent)

The checker re-derives everything: invariants → leakage audit → cascade →
falsification battery → deflated Sharpe with the ledger's true trial count.
Writes the verification artifact to `outputs/`, THEN the labeled finding
(the PreToolUse hook enforces artifact-before-promotion and checker ≠ maker).
High-stakes candidates additionally go to `research-skeptic` for refutation;
survivorship of an honest attack is evidence.

## Stage 5 — SELECT

Among validated candidates: prefer the one that survives the skeptic with the
best *robustness* profile (noisy-knob retention, regime breadth), not the best
point estimate — top-of-ranking on noisy estimates systematically disappoints
(shrink before you rank). Record Pass@k vs the selected candidate's rank in
the ledger notes.

## Stage 6 — REPORT

Disclaimer-bearing research report (templates/daily_report or weekly_report):
findings cited by pointer (finding id + artifact path), label + confidence
per docs/label_policy.md and docs/report_policy.md, verification-debt items
listed, `needs_human_review` queue surfaced. The human decides; the report
never recommends an action.

## Standing rules

- Trajectory hygiene: after any error, one action per turn; no
  "finding confirmed" without an executed artifact (hook-enforced); judge
  long trajectories with the `trajectory-judge` skill before trusting them.
- All stored sets in canonical order (`project_money.memory.canonical_sort`);
  reads via order-invariant aggregation.
- Canonical labels only, everywhere.
