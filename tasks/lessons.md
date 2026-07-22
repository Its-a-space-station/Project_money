# Lessons — Project_money

> Append durable insights a future session would be worse off not knowing. Prefer
> adding a dated note over rewriting history. Not executable automation.

## Format

```text
### YYYY-MM-DD — Short title
**Context:** what we were doing.
**Lesson:** what we learned.
**Apply:** how to act on it next time.
```

## Workflow lessons

### 2026-07-20 — Adopted the Decision Systems Playbook (tailored bootstrap)

**Context:** Project_money began as a single quant-research brief (`.rtf`). We
adopted the shared playbook's structure, architecture, and philosophy.
**Lesson:** The playbook is a *governance layer* meant to be inherited; the
project's own quant doctrine is the *domain layer*. They compose cleanly when
kept as distinct parts of `CLAUDE.md` with safety rules taking precedence.
**Apply:** When pulling in more playbook layers later (v2 forecasting, macro),
keep governance vs. domain separation and re-run the cross-link check.

### 2026-07-20 — Localize + link-trim when inheriting shared docs

**Context:** Adopting the playbook copied docs written for a *family* of systems;
they carried sibling-system examples (eBay/Minervini/Polymarket/Kalshi/IBKR) and
cross-links to uncopied v2 layers.
**Lesson:** Verbatim inheritance leaves two defects — dangling cross-links to files
you didn't copy, and sibling references that misread this repo as multi-system.
**Apply:** After any future playbook pull, (1) run a repo-wide relative-link scan
and trim/repoint links to uncopied targets, and (2) grep for sibling-system names
and localize them to Project_money. Both were run this session and are green.

### 2026-07-20 — Fan-out prompts must say "this list is yours alone"

**Context:** Six parallel reading agents were launched over paper clusters. One
agent read a single paper, then stopped — assuming the rest of *its own* list was
covered by "the other agents" it inferred from context.
**Lesson:** A subagent that knows it is part of a fan-out may wrongly assume
overlap and under-deliver. Exclusivity of assignment must be explicit.
**Apply:** In every multi-agent fan-out prompt, state that the listed items are
the agent's exclusive assignment, no other agent shares them, and the final
message must satisfy the full output contract for every item.

## Safety lessons

### 2026-07-20 — Robinhood is a broker, not just a data API

**Context:** The original brief lists a "Robinhood API" as an available resource.
**Lesson:** Robinhood's SDK also exposes order/fund execution endpoints. Under the
playbook, a broker is a **read-only, gated data provider** and never an action
sink; capability existing is not authorization.
**Apply:** Any Robinhood usage is read-only data only, isolated from any code that
could act, gated behind [docs/broker_strategy.md](../docs/broker_strategy.md).
Never instantiate an execution client.

## Project-specific lessons

### 2026-07-20 — Lookahead detectors must compare the whole window, not the boundary

**Context:** First test run of the verification backbone: a full-sample
z-scoring leak escaped the lookahead check.
**Lesson:** Comparing only the cutoff row misses leaks that thresholding hides
at the boundary — contamination from full-sample statistics shows up at
*earlier* dates. Causality means every overlapping row must match under
truncation.
**Apply:** `check_no_lookahead` compares the entire truncated output against
the full-sample slice. Any future causality check should follow the same
whole-window rule — and keep the bracket pair (causal signal passes, leaky
signal fails) as permanent tests.

### 2026-07-20 — A draw from the null WILL sometimes top its own null

**Context:** A "noise must not stand out" test failed on one seed: the IID
series legitimately landed in the top 2% of its own permutation distribution.
**Lesson:** Single-draw assertions against a null distribution are flaky by
construction (the draw is from that null). This is the unit-test version of
selection-on-noise — the same trap the deflated-Sharpe machinery guards
against in research.
**Apply:** Test null behavior across many seeds with a loose bound on the
stand-out *rate*, never a single-seed percentile assertion. Never fix such a
test by picking a friendlier seed.

### 2026-07-20 — An enforcement boundary is an attack surface: fail closed, normalize paths, cover every write route

**Context:** Adversarial review of the finding-promotion hook found six
independent bypasses (exception → fail-open, `./`-relative paths, case
variants on APFS, subdir cwd, Bash shell writes, `*README.md` suffix
exemption) plus a vacuous-evidence hole (any existing file as "artifact").
**Lesson:** A gate's unit tests proving it blocks the obvious bad case say
nothing about the routes *around* it. Gates need: fail-closed error handling,
normalized root-anchored path matching, coverage of every tool that can
produce the guarded effect, and evidence checks on content (parseable
artifact under the expected directory), not mere existence.
**Apply:** Bracket-test the gate itself AND red-team it (the review's
"cheat any way you can" pass found what bracket tests missed). Any new hook
or gate gets the same adversarial pass before it is trusted. This mirrors the
corpus finding that verifier-hardening is the core design, not polish.

### 2026-07-20 — A guard hook you install is live against your own commands; match on target, not keywords

**Context:** The Bash findings-guard, once wired into `.claude/settings.json`,
blocked my own `git commit` — its first heuristic flagged any command where
"findings" and a write-indicator (`>`) merely co-occurred, and the commit
message mentioned both.
**Lesson:** (1) PreToolUse hooks in the project settings apply to this
session's own tool calls, including git — a badly-scoped guard blocks
legitimate work. (2) Keyword co-occurrence is the wrong model for a write
guard; match the write *construct targeting* the protected path (redirection
into it, cp/mv with it as the destination arg), so commands that only mention
or read the path pass.
**Apply:** Scope PreToolUse guards to the actual dangerous construct, add
false-positive regression tests (a git-commit message, a read, a source-side
`cp`) alongside the true-positive ones, and remember the guard runs against me.

### 2026-07-21 — Verify implemented formulas against their primary sources before gating on them

**Context:** Batch-3 verification found our deflated-Sharpe benchmark used
`sqrt(1/n_periods)` where the source requires the empirical cross-trial
variance of Sharpe estimates — making the promotion gate anti-conservative
exactly for diverse trial sets (the dangerous direction). A second hazard:
the formula takes raw kurtosis but our metrics emit excess.
**Lesson:** A "simplified" implementation of a published statistic can invert
its safety properties. Convention mismatches (raw vs excess kurtosis,
annualized vs per-period) are silent corrupters at interface boundaries.
**Apply:** Any statistic used as a gate gets (a) a verify-against-source pass
before first reliance, (b) input validation that catches convention mistakes
mechanically (the kurtosis<1 guard), and (c) a regression test encoding the
directional behavior the source requires (diverse trials ⇒ higher bar).

### 2026-07-21 — Fleet digests are testimony, not evidence: spot-check numbers before they become load-bearing

**Context:** The batch-4 synthesis quoted Exchange-720 figures from a reading
agent's digest (NLinear 0.409, Repeat 0.601) as its flagship "linear beats
deep on financial data" exhibit. An independent checker pass against the
corpus PDF refuted them: actual NLinear 1.033 / Repeat 0.823 MSE — "0.601"
was DLinear's *MAE* — and the "N-HiTS loses to NLinear/Repeat" comparison was
inverted (only DLinear 0.643 beats N-HiTS 0.798 there).
**Lesson:** A reading agent can mix table columns (MSE vs MAE) or paper
versions, and the error propagates silently into a synthesis where it becomes
a headline exhibit. The *direction* survived here; the specific numbers did
not — the dangerous case, because a plausible direction hides a wrong number.
**Apply:** Before any number from a subagent digest becomes load-bearing in a
synthesis or finding, have an independent checker re-open the source and
confirm the exact cell (metric, row, version). Restrict load-bearing exhibits
to checker-verified figures and mark the rest as digest-sourced. This is the
documentation-layer instance of maker ≠ checker — it has now paid off in two
consecutive batches (DSR formula in batch 3, Zeng figures in batch 4).

### 2026-07-21 — Never pre-label evidence with the checker's imprimatur

**Context:** The batch-5 synthesis draft labeled its central exhibit
"(checker-verified)" at drafting time — before the checker had been
launched. The subsequent independent pass happened to confirm those numbers
(8/10 confirmed, 2 with corrections, 0 refuted), but the label was written
on credit.
**Lesson:** Writing "checker-verified" (or any verification status) before
the check runs is self-attestation wearing the checker's uniform — the
worst kind, because it *looks* like process compliance. If the checker had
been skipped or interrupted, the false label would have survived into the
committed record.
**Apply:** Verification-status labels are written only *after* the
verification event, by reference to its actual outcome ("independently
checker-confirmed after drafting — see provenance"). Draft-stage claims
carry `validation_pending` or no label. The provenance section records the
checker's real score, including what it corrected.

## Repeated mistakes to avoid

- Treating an available API/credential as authorization to use its write paths.
- Promoting a self-attested result past `validation_pending` without an
  independent checker.
- Using action words (buy/sell/trade/order) as labels or field names.
