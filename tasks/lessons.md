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

## Repeated mistakes to avoid

- Treating an available API/credential as authorization to use its write paths.
- Promoting a self-attested result past `validation_pending` without an
  independent checker.
- Using action words (buy/sell/trade/order) as labels or field names.
