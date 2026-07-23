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

### 2026-07-22 — A big fan-out that keeps dying on limits wants a resumable Workflow, not repeated Agent fan-outs

**Context:** Batch 6 (73 papers, 8 reading agents) was attempted three times.
Attempts 1–2 used loose Agent fan-out on Fable 5 and both died mid-run — first
on a monthly-spend limit, then on credit exhaustion — with no cluster
finishing and nothing salvageable; each restart re-read everything. Attempt 3
ran the identical work as a Workflow (resumable, per-cluster verify built into
the pipeline) and completed cleanly (16 agents, 0 errors).
**Lesson:** For a large, expensive fan-out that has already shown it can die
partway (limits, flaky API), the loose-Agent pattern has no recovery — a
restart pays full cost again. A Workflow caches completed agents and resumes
the unfinished ones, and it folds the checker stage into the same run.
**Apply:** When a fan-out is (a) large, (b) expensive, and (c) at real risk of
mid-run failure, prefer the Workflow tool with its resumeFromRunId recovery
over N independent Agent calls. Keep the loose-Agent pattern for small or
cheap fan-outs where a restart is trivial. (Ultracode also directs Workflow
use by default when on.)

### 2026-07-22 — A proposed detector can pass "sounds right" and fail verification — check the alarm's own logic

**Context:** A batch-6 reading agent proposed a "pretrained-vs-from-scratch
performance-gap alarm": flag benchmarks where pretrained-LLM forecasters
cluster far above from-scratch models on pre-cutoff data, as a contamination
smell. The verify pass refuted it: on the same StockNet window several
*from-scratch* DL models also reach ~0.07 MSE, so low MSE is not a reliable
contamination signature — the clustering argument does not hold.
**Lesson:** Not every plausible-sounding verifier idea survives its own
evidence. This one would have produced false contamination flags on clean
from-scratch models. The underlying *gate* it was meant to support (reject
results where the model's training cutoff overlaps the eval window) is sound;
the *alarm heuristic* built on top of it was not.
**Apply:** Before cataloguing a proposed check as an adoption, verify the
check's own discriminating logic against the data it claims to separate — the
same maker≠checker rigor we apply to findings applies to the tools that judge
findings. Record rejected-on-verification proposals explicitly so they aren't
silently re-proposed.

### 2026-07-22 — A correct aggregate can hide a wrong membership; keep the synthesis-level checker

**Context:** The batch-6 synthesis said "the 10 credible papers" and listed 10
— but two were PARTIAL-tier (AlphaGen, VTA) swapped in for two genuinely
CREDIBLE-tier papers (Nexus, AI-Analyst) that were dropped. The count "10" was
right; the *membership* was wrong. The independent synthesis-level checker
caught it. This is the THIRD consecutive batch where the synthesis step (my
own writing) introduced an error the verified digests did not contain —
batch 4 mixed MSE/MAE columns, batch 5 pre-labeled evidence "checker-verified"
before the check, batch 6 mis-assigned tier membership.
**Lesson:** (1) A correct total is not evidence of a correct set — verify
membership/labels, not just sums (a two-for-two swap conserves the count).
This is exactly the label-consistency failure label_policy exists to prevent.
(2) The maker≠checker step must run on MY synthesis, not only on the
subagents' digests: the digests were all verified, yet the integration on top
of them still shipped a defect three times running. The synthesis-level
checker has now paid for itself in three of three batches — it is not optional.
**Apply:** After writing any synthesis that assigns items to labeled buckets,
independently re-derive both the counts AND each item's bucket against the
source tiering before the doc is relied on. Always run a checker on the
integrating document, not just on its inputs.

### 2026-07-22 — Project pivoted to research-AND-trading; the operative invariant is the division of labor, not "research-only"

**Context:** The project was scoped "research-only, execution never, Robinhood
read-only." The user corrected that: the actual intent was always automated
execution of validated strategies via Robinhood (a prior session built exactly
such a guardrailed bot for Kalshi). CLAUDE.md + safety_policy + broker_strategy
+ the rest of the governance docs were rewritten to match.
**Lesson:** "Research-only" is no longer the invariant — but the safety substance
did not disappear, it changed shape. The invariant that now carries the safety
load is the **division of labor** (safety_policy.md §1): the assistant builds,
tests, and validates; the **human operates live capital** — the assistant never
itself places a live order, moves funds, flips a system to live, or handles live
credentials, and autonomy is always bounded/observable/stoppable/validation-gated.
A prior build (Kalshi) is not license for the assistant to operate live capital or
hold credentials — those lines hold regardless of precedent.
**Apply:** A future session must NOT re-impose blanket "research-only" (it's
stale), and must NOT drift the other way into the assistant executing/operating
live. Read STATE.md for the current authorized phase — execution is the gated
*destination*, and each phase (dry-run → paper → shadow-canary → human-approved
live → bounded auto-trade) begins only on explicit authorization recorded in
STATE.md. Validation always precedes capital.

### 2026-07-22 — Edge before infrastructure: no execution bot until a validated edge exists (the Kalshi lesson)

**Context:** The user's prior project built a complete, well-guardrailed Kalshi
trading bot *first*, then discovered there was no durable discoverable edge, and
the project stalled — effort sunk into machinery with nothing valid to run. The
user explicitly does not want to repeat that pattern in Project_money.
**Lesson:** Execution infrastructure has ~zero value without a validated strategy
to execute. Building the bot first inverts the risk. Our own six-corpus intake
independently found discoverable daily-horizon edges are rare and the impressive
ones are usually contaminated — which makes "infra-first" especially dangerous
here. This is a recurring, cross-project pattern, not a one-off.
**Apply:** Sequence **edge-first**. The execution build (any Robinhood order path)
is gated behind a strategy that has actually cleared the full verification stack —
not merely behind a phase authorization. Recorded in STATE.md approved-decisions
(2026-07-22). If validation yields no survivor, that is a valid, money-saving
outcome (correct rejection), never a problem to route around by building the bot
anyway. The next build work is the research/validation engine + verifier
hardening (S1–S30), aimed at honestly answering "is there an edge?" — and being
willing to answer "no."

### 2026-07-22 — Execute-and-compare detectors assume a PURE signal_fn; state defeats them

**Context:** Building the S6 intra-bar leakage detector (`check_intrabar_causality`,
execute-and-compare like `check_no_lookahead`). Two red-team rounds found that a
signal_fn which *memoizes its output keyed by date* passes cleanly: the first call
(the base) caches the real leak, and every perturbed call returns the stale cached
value, so base == perturbed and no leak is detected. The determinism pre-check
(same input twice) does not catch it — a cache handles identical input happily.
This blind spot applies to **`check_no_lookahead` too** (it re-runs signal_fn on
truncated data and assumes purity); it is a property of the whole
execute-and-compare family, not one detector.
**Lesson:** Any "re-run the function and compare outputs" causality check silently
assumes the function is a *pure* function of its input. Statefulness (memoization,
call-count logic, global caches) breaks that assumption and cannot be fully
certified in-process — the true fix is process/object isolation. A partial defense
that catches the common index-keyed case: run the perturbation on a **cold-reindexed
copy** (a disjoint index, *distinct per call* — reusing one cold index lets the
memoizer cache the probe itself), so a date-keyed cache must recompute; flag a
divergence *distinctly* ("appears stateful/impure or calendar-dependent — cannot
certify"), never silently as "leakage."
**Apply:** (1) State the purity precondition explicitly in every execute-and-compare
detector's docstring. (2) Add a cold-reindex statefulness probe with a fresh index
per call. (3) Treat full adversarial-statefulness certification as **verification
debt** whose real fix is isolation — record it, don't pretend the in-process gate
closes it. (4) When a red-team fix is itself non-trivial (the probe had a
cache-warming bug), re-verify the fix, not just the original hole.

### 2026-07-22 — A verifier's own sampling/tolerance knobs are attack surfaces

**Context:** The first S6 draft had a fixed evenly-spaced test grid (a leak could
zero itself exactly at the tested bars — recomputable and gameable), a fixed
±2/5% perturbation band (blind to threshold leaks and un-scaled to volatility),
and an `atol + rtol*|value|` comparison (a large DC offset inflated the tolerance
so a sub-tolerance leak recovered by a downstream demean+sign slipped through).
All three were demonstrated bypasses.
**Lesson:** A verifier's internal parameters — *which* points it samples, *how far*
it perturbs, *what tolerance* it compares at — are part of its attack surface, just
like a gate's error handling (2026-07-20 lesson). A recomputable sample set is
dodgeable; a fixed perturbation band has blind zones; a relative tolerance scaled
by |value| is inflatable by an offset. Deterministic-but-recomputable sampling
trades reproducibility against un-gameability and cannot fully satisfy both — the
fast-path subsample is best-effort, and exhaustive is the trustworthy mode.
**Apply:** Prefer exhaustive checking where affordable (no sample to game); make
perturbations wide and data/vol-scaled (span the field's realized range both ways);
compare causal invariance at a *tight absolute* tolerance (a truly causal output is
bit-identical when unused inputs change) plus a scale-invariant sign check. Where a
knob must trade safety for speed, document it as best-effort and record the residual
as verification debt.

### 2026-07-22 — Gate against the null, not a fixed threshold; never let self-attested metadata disable a check

**Context:** The first S5 forecast-diagnostic used a fixed bar (R² > 0.95 on
levels) gated on a caller-supplied ``is_levels`` flag. Red-team broke it two ways:
(1) a near-perfect level leak degraded to R²≈0.94 sailed under the fixed bar
(R² and lag-corr both measure fit, so they move together — no independent
backstop); (2) flipping ``is_levels=False`` disabled the R² check entirely, so an
R²≈0.9999 "returns forecast" passed. It also false-flagged legitimate AR/momentum
returns forecasts (corr(ŷ_t, r_{t-1})=1 is signal on returns, not persistence).
**Lesson:** (a) A fixed metric threshold is a line an optimizer tunes right up to;
the honest test compares against the relevant **null** — for near-integrated
levels, skill vs the persistence forecast (levels already score R²≈0.99, so
"beats persistence" is the real bar, and a degraded leak scores *negative* skill).
(b) **Never let candidate-supplied metadata gate the existence of a check** —
infer the property yourself (level-ness from the target's lag-1 autocorrelation)
and keep an unconditional implausibility flag. (c) A check that fires on a
legitimate strategy family (calendar seasonality, AR/momentum) is as harmful as a
miss — scope it to where the failure mode actually applies.
**Apply:** Design every gate as "beats the honest null by a margin," not "clears a
fixed metric." Infer, never trust, the flags that decide which checks run. Pair
each new detector's specimen (must-fail) with a legitimate near-neighbor
(must-pass) so false positives surface in the bracket test.

### 2026-07-23 — NaN fails a naive numeric gate OPEN; sibling gates must fail the same way; recompute, don't trust reports

**Context:** Red-team of the S11/S16 plausibility gates. S16's floor check
`cost_bps < 5.0` let `float('nan')` through (`nan < 5.0` is False), and its vanish
check (`gross > 0 and net <= 0`) let an all-NaN payload pass with zero reasons —
so a broken/undefined cost model read as "cost-inclusive, edge survives." Its
sibling S11 correctly fail-closed on NaN, so the two gates failed in *opposite*
directions. Separately, S16 compared self-reported scalars (`cost_bps`,
`sharpe_net`) and so certified fabricated numbers, and `net == gross` (a cost
provably not applied) as cost-inclusive. And both gates are one-sided *upper*
alarms — a zero-skill coin-flip (S11) and a zero-edge no-op (S16) pass them.
**Lesson:** (1) Every numeric comparison in a gate is a NaN fail-open unless
guarded — `x < bar` and `x > 0` are both False for NaN. Guard with
`math.isfinite` and fail closed. (2) Sibling gates must fail in the same (closed)
direction; a fail-direction inconsistency between two checks is itself a defect.
(3) A gate that reads a reported scalar certifies whatever the candidate reports —
recompute the metric from the primitive artifacts (weights + returns), matching
the metrics-doctrine ("recomputed from artifacts, never accepted from a report").
(4) A one-sided alarm ("too high"/"too low") is not a standalone screen: "passed"
≠ "has an edge and is clean." Compose alarms with the edge-existence gates
(deflated Sharpe / multiplicity, no-lookahead) before promotion.
**Apply:** Add an explicit non-finite → fail-closed guard to every gate; unit-test
the NaN/None/inf case for each. Prefer artifact-recompute over reported scalars.
Bracket-test both legs (oracle passes / garbage fails) AND ask "what no-op passes
this?" — if a trivial null passes, the gate is one-sided and must be composed, not
trusted alone.

### 2026-07-23 — Binary pass/fail conflates "reject" with "route to human review"

**Context:** S11 (and S5's returns bar, S10) are documented as *review* flags
("mandatory audit"), but `CheckResult` is binary and `run_cascade` maps any
`passed=False` to `label='reject'` — so wiring them as cascade stages would
hard-reject legitimate strategies (a 62%-accuracy trending base rate, a strong
returns edge) instead of routing them to `needs_human_review`.
**Lesson:** Some checks are hard rejects; others should route to human review. A
binary pass/fail cannot express that tri-state, and the difference is
label-load-bearing (`reject` vs `needs_human_review` — both canonical). The
disposition is a property the check must carry, not something the cascade can infer.
**Apply:** When integrating these checks into the cascade, give review-disposition
checks (S11, S5 returns bar, S10, S16 rate-advisory) a machine-readable
"needs_human_review" disposition rather than registering them as rejecting stages.
Tracked as verification debt in `tasks/todo.md` until the cascade wiring exists.

## Repeated mistakes to avoid

- Treating an available API/credential as authorization to use its write paths.
- Promoting a self-attested result past `validation_pending` without an
  independent checker.
- Using action words (buy/sell/trade/order) as labels or field names.
