# STATE.md — Project_money

> A living snapshot of this project. Update it whenever the phase, scope, or
> constraints change — it is the first thing a new session reads after `CLAUDE.md`.
> Not executable automation.

*Last updated: 2026-07-22.*

## Phase

**Research build authorized 2026-07-22 (user, in-session).** The 1–4 ungating is
recorded (see Approved decisions) and the **first research build phase — verifier
hardening (S1–S30 / V1–V8 / W1–W6) → read-only Tiingo/FRED data → cached MVP
screen — is authorized.** Scope is lifted toward **research work only**; **no
execution path is authorized** — any Robinhood order path, fund movement, or live
scheduling stays gated behind a validated survivor (edge-first sequencing). Build
is underway (verifier hardening first).

**Tooling build (research-tooling code authorized 2026-07-20).** The playbook
bootstrap is complete and the first tooling code exists under `src/project_money/`
with a green deterministic test suite (`tests/`, 170 tests): verification backbone
(invariants incl. lookahead detector, metrics + deflated Sharpe, walk-forward,
prequential codelength, evaluation cascade), leakage/vintage auditor,
metric-falsification harness, hypothesis ledger + tabu memory, MDL complexity
gate.

**Scope corrected 2026-07-22: research-AND-trading.** The project's destination is
**human-operated automated execution of validated strategies via Robinhood**,
built through a gated ladder (dry-run → paper → shadow-canary → human-approved
live → later bounded auto-trade). CLAUDE.md and the safety/broker/report/label
docs were rewritten to match. **This corrects scope only — it authorizes no new
build.** The current authorized state is unchanged: research-tooling code is
built; **provider adapters, broker/execution code, and every execution phase
remain separately gated and begin only on explicit authorization recorded here.**

## Current MVP scope

- **Immediate (once authorized):** a deterministic, reproducible research +
  validation slice on cached data — the smallest verifiable strategy screen with
  maker/checker separation and canonical labels, plus a report. This is the
  proving ground the execution ladder is gated behind.
- **The destination (gated, phased):** validated strategies executed via Robinhood
  under the human-operated ladder in [docs/broker_strategy.md](docs/broker_strategy.md)
  §3, with the full guardrail set (kill-switches, position/loss limits,
  shadow-canary, journaling/reconciliation, dry-run) before any real money.
- **Now authorized (2026-07-22, research scope only):** verifier hardening
  (S1–S30 / V1–V8 / W1–W6), **Tiingo + FRED read-only** adapters with a
  point-in-time cache, bounded strategy/factor search, paper-candidate forward
  tracking, the cached MVP screen.
- **Still gated (each a separate gate):** any Robinhood data or execution path,
  fund movement, live scheduling, machine-learning / forecasting models, options
  and cross-asset modeling. Execution stays gated behind a validated survivor
  (edge-first).

## Approved decisions

- 2026-07-20 — Convert the original `.rtf` brief into `CLAUDE.md`.
- 2026-07-20 — Adopt the Decision Systems Playbook via *tailored bootstrap* and
  *merge* the quant-research philosophy into `CLAUDE.md` (governance layer +
  domain layer in one file; safety rules win on conflict).
- 2026-07-20 — **Build all three tool packages** from
  [docs/agent_tooling_synthesis.md](docs/agent_tooling_synthesis.md) §4
  (user-selected: Pkg 1 verification backbone, Pkg 2 research loop, Pkg 3
  infra & memory).
- 2026-07-20 — **Scope guard partially lifted: research-tooling code is
  authorized** (harnesses, checkers, ledgers, registries, tests). Still
  excluded and separately gated: provider/data adapters, broker code, any
  execution path, live scheduling. No secrets; deterministic tests only.
- 2026-07-22 — **Project scope corrected: research-and-trading, not
  research-only.** The destination is human-operated automated execution of
  validated strategies via Robinhood, built through the gated ladder
  ([docs/broker_strategy.md](docs/broker_strategy.md) §3). CLAUDE.md +
  safety_policy + broker_strategy + report_policy + label_policy rewritten to
  match. Invariants preserved: the assistant builds/validates but never itself
  executes live, moves funds, flips to live, or holds credentials; autonomy is
  bounded/observable/stoppable; validation precedes capital. Reference guardrail
  design = the user's Kalshi trading bot. **This decision corrects scope; it does
  NOT authorize beginning any execution build — each phase still requires explicit
  authorization recorded here.**
- 2026-07-22 — **Edge-first sequencing (the Kalshi lesson).** No Robinhood
  execution build begins until (a) the research/validation engine is complete and
  (b) at least one strategy has actually cleared the full verification stack — a
  **discovered, validated edge exists.** The prior Kalshi project built the bot
  first, found no discoverable edge, and stalled; we do not repeat that. Execution
  is gated not merely behind phase authorization but behind **a survivor.** If
  validation yields no survivor, **no bot is built** — correct rejection is the
  intended, money-saving outcome (CLAUDE.md §11, §20). The next build work is
  therefore **edge discovery** (research engine on real data + the S1–S30 verifier
  hardening), never the execution path.
- 2026-07-22 — **1–4 ungating RECORDED and first research phase AUTHORIZED (user,
  in-session).** Scope guards lifted toward **research work only**: (1)
  deterministic MVP on cached data, (2) **Tiingo + FRED read-only** adapters with a
  point-in-time / vintage-safe cache, (3) bounded strategy/factor search, (4)
  paper-candidate forward tracking (`frozen_at`, strictly-post-timestamp scoring).
  **First build phase authorized:** verifier hardening (S1–S30 / V1–V8 / W1–W6) —
  lead with the known-bad specimen fixtures + calibration axis (S26) +
  leakage-detector GAPS (S6/S7/S8) — then read-only provider data, then the cached
  MVP screen. **NOT authorized (unchanged):** any Robinhood data or execution path,
  fund movement, live scheduling, ML/forecasting models, options/cross-asset —
  execution stays gated behind a **validated survivor** (edge-first). Invariants
  unchanged: the assistant builds/validates and never executes live or holds
  credentials; validation before capital; bounded/observable/stoppable autonomy;
  no secrets.

## Safety rules (in force)

- **Division of labor:** the assistant builds and validates; the **human operates
  live capital.** The assistant never itself places a live order, moves funds,
  flips a system to live, or handles live credentials (safety_policy.md §1).
- **Validation before capital:** no strategy reaches live money without clearing
  the full verification stack (maker ≠ checker, deflated Sharpe, leakage /
  contamination audit, cost-inclusive eval, forward tracking).
- **Bounded, observable, stoppable autonomy:** any execution runs inside hard
  limits + kill-switches, fully journaled and reconciled, instantly haltable. No
  unbounded or unattended autonomy.
- **Phased, each step gated:** dry-run → paper → shadow-canary → human-approved
  live → (later) bounded auto-trade; each phase begins only on explicit
  authorization recorded here.
- **No secrets** in the repo; credentials human-supplied at runtime.
- Research-layer canonical labels only (docs/label_policy.md); execution
  vocabulary confined to the gated execution module.

## Non-goals

- **Assistant-executed trades or assistant-held credentials** — permanent; the
  human operates live capital, always.
- **Unbounded or unattended autonomy** — permanent; all automation stays limited,
  journaled, and kill-switchable.
- **Live money on an unvalidated strategy** — permanent; validation precedes
  capital.
- Beginning any build phase (providers, broker data, execution) without explicit
  authorization recorded above. Execution is the gated *destination*, not a
  current non-goal.
- No v2 / v2.1 / v2.2 playbook layers (forecasting, macro, object-memory) adopted
  yet — available to pull in later if authorized.

## Active loops

None. When built: research/monitoring loops produce findings and reports; an
execution loop (Phase 6, separately authorized) runs only within hard limits +
kill-switches, journaled and instantly haltable — never unbounded or unattended.

| Loop | Cadence | Bounds / stop conditions | Status |
| --- | --- | --- | --- |
| — | — | — | none |

## Blockers

- None. Next steps are gated on explicit user authorization, not blocked.

## Last checkpoint

- 2026-07-23 — **S11/S16 red-team hardening committed (3rd checkpoint).** The
  metric-plausibility/cost gates had real logic defects (S16 fail-OPEN on NaN;
  trusted reported scalars; accepted net==gross; S11 crashed on a non-float) — all
  fixed: math.isfinite fail-closed, artifact recompute (recompute-don't-trust),
  net≥gross rejection, dropped the FP-prone rate floor. 13 gate tests. Two durable
  lessons recorded (NaN fail-open + sibling fail-direction; binary pass/fail
  conflates reject vs needs_human_review). **All six detectors now red-teamed to
  convergence.** Suite: **234 passed, 1 xfailed**, deterministic. Committed to
  `main`, not pushed.
- 2026-07-23 — **Calibration-first milestone: ALL FIVE §9 known-bad specimens are
  now rejected by the harness.** Added the Paper 8 gates (S11 impossible-accuracy
  alarm + S16 cost gate, `validation/metric_plausibility.py`; its scaler-leak is
  caught by the existing `check_no_lookahead`) and applied the S5 round-3 fixes
  (returns R² bar raised to 0.5 and framed as review to avoid killing a rare
  strong edge; integratedness hysteresis). S6/S9/S5/S10 red-teams **converged over
  3 rounds each**; S11/S16 red-team running. Suite: **229 passed, 1 xfailed**,
  deterministic. Verification debt extended (S5 abstain-regime honesty gap;
  contemporaneous-leak delegation to execution-lag + S6 + walk-forward, with a
  TODO for a dedicated red-team of that; S5 returns bar is a review flag). Pure
  research-tooling; no provider/execution/secrets. Second checkpoint committed to
  `main`, not pushed.
- 2026-07-22 — **Verifier-hardening checkpoint committed (research phase 1 in
  progress).** Built S6 (intra-bar contemporaneous leakage), S9 (temporal
  split-integrity), S5+S10 (forecast diagnostics), and verified S3 (MarketSenseAI
  via the existing vintage auditor) — closing **4 of the 5 §9 known-bad
  specimens** (remaining: Paper 8 compound). Every detector adversarially
  red-teamed (S6 ×3 rounds; S9/S5/S10 ×2 rounds, round-3 running at commit time):
  ~16 real holes found and fixed, each kept as a permanent regression specimen.
  Suite: **220 passed, 1 xfailed** (documented compute-once-cache isolation
  limit), deterministic. Verification debt tracked (max_test_bars best-effort;
  adversarial statefulness needs isolation). Pure research-tooling — no
  provider/execution paths, no secrets. Committed to `main`, not pushed.
- 2026-07-22 — **1–4 ungating recorded + first research phase (verifier hardening)
  authorized by the user in-session.** Research-scope guards lifted (cached MVP,
  Tiingo/FRED read-only, bounded search, forward tracking); execution stays gated
  behind a validated survivor. Build kicked off with localization of the
  S1–S30 / V1–V8 / W1–W6 spec against the current harness, then the known-bad
  specimen fixtures (fail-before/pass-after). No secrets; no provider/execution
  write paths. Suite baseline: 170 green.
- 2026-07-22 — **Information batch 6 ingested — FINAL BATCH; end-of-information
  signal received** (73 stock-market ML/AI papers, eight adversarial-triage
  agents + inline per-cluster verification + a synthesis-level checker):
  [docs/stock_market_synthesis.md](docs/stock_market_synthesis.md). Direct-
  domain, highest junk-density: **CREDIBLE 10 · PARTIAL 23 · JUNK 33 · OTHER
  7**. Verdict: **zero validated tradeable daily-horizon edges across 73
  papers** — the strongest in-domain confirmation of the whole doctrine (the
  10 "credible" papers are credible as methods/exemplars only). Yield: the
  **S1–S30 verifier/policy additions** (six are new leakage-detector GAPS:
  intra-bar contemporaneous leakage, non-causal decomposition, non-causal
  feature construction, calibration/process-fidelity axis, synthetic-feature
  label leakage, horizon-monotonicity), a vintage-tagged dataset catalog, and
  search discipline for the bounded search. Run as a resumable Workflow
  (`wf_f7d99529-662`) after two Fable attempts died on spend/credit limits.
  Verification: **57 claims → 52 confirmed, 5 corrected, 0 refuted**; one
  proposed detector rejected on verification (recorded). Suite: **170 tests
  green** (no code changed). **NOT committed; ungating NOT recorded.**
- 2026-07-21 — **Information batch 5 ingested** (25 graph-ML papers, five
  fresh-read agents + one independent checker):
  [docs/graph_ml_synthesis.md](docs/graph_ml_synthesis.md). New territory
  (zero playbook overlap) → fresh-read pattern. Verdict: **refines rather
  than expands** — no capability case for graph ML on our panels; batch-4
  MTGNN verdict confirmed + boundary-corrected (masked attention is O(d);
  condemned by SNR economics, not multiplicity); W1–W6 verifier queue joins
  V1–V8 (known-positive controls, split-key provenance, cheap-heuristic
  nulls, search-space DSR accounting, stratified noise probes, capacity
  matching); distill-then-validate symbolic pipeline pre-specified as the
  future route for flexible ML; 14-entry do-not-build ledger. Checker: 10
  load-bearing claims — 8 confirmed, 2 corrected, 0 refuted; caught the
  maker pre-labeling evidence "checker-verified" before the check ran
  (lesson recorded). Ungating verdict: **sharpens, does not reorder**.
  Suite: **170 tests green**. Not yet committed.
- 2026-07-21 — **Information batch 4 ingested** (26 time-series-forecasting
  papers, five verify-and-extract agents + one independent checker):
  [docs/ts_forecasting_integration.md](docs/ts_forecasting_integration.md).
  The playbook's **unadopted** v2.1 forecasting layer passed its source
  audit (third successful independent playbook audit): 1 hard defect
  (Time-LLM listed as a probabilistic source; it is point-only), 1 cross-doc
  inconsistency (ARIMA-vs-DLinear null ordering), 9 wording + 4 attribution
  corrections — all recorded as **adoption prerequisites**, since the layer
  stays unadopted. Checker pass on the synthesis corrected two
  digest-sourced numbers before reliance (lesson recorded). Outputs: V1–V8
  verifier build items queued alongside the batch-3 follow-ons; fleet-ops
  updates; pre-specified (still-gated) forecasting protocol. Ungating
  verdict: **sharpens, does not reorder** the agreed 1–4 plan. Suite: **170
  tests green**. Not yet committed.
- 2026-07-21 — **Session handoff written**: [HANDOFF.md](HANDOFF.md) — full
  session summary (bootstrap → tooling build + adversarial review → three
  information batches → gate corrections) and next steps. Information intake
  is ONGOING (user still uploading); the agreed 1–4 ungating remains
  deliberately unrecorded until the user's end-of-information signal. Suite:
  170 tests green at commit `8d499c2` (pushed).
- 2026-07-20 — Playbook adopted; docs self-consistent; schemas set to
  `project_money`; scaffolding and blueprint written. Original `.rtf` brief
  deleted (absorbed into `CLAUDE.md`); all inherited docs localized to
  Project_money (no sibling-system references remain). First commit pushed to
  GitHub (`origin/main`).
- 2026-07-20 — **Tooling pre-phase:** six-agent mechanism-level review of the
  38-paper coding-agents corpus completed;
  [docs/agent_tooling_synthesis.md](docs/agent_tooling_synthesis.md) written
  (10 design principles, 11 proposed tools in 3 packages, finance-specific
  cautions). Independent cross-check confirmed the playbook's 2026-07-19 paper
  map with no contradictions.
- 2026-07-20 — **All three packages built.** Pkg 1 verification backbone +
  Pkg 2 cores (commit `e32a967`), then the config layer: subagent roles,
  research-pipeline + trajectory-judge skills, finding-promotion hooks,
  tool registry, tool-factory admission gate, memory/ordering helpers,
  object-memory + skill-evolution policy docs. An 82-agent adversarial review
  (4 lenses, 2-skeptic verification) confirmed 32 defects — all fixed with
  regression tests; **163 tests green, deterministic** (commit `803be80`,
  pushed).
- 2026-07-21 — **Information batch 2 ingested** (28-book trading corpus, six
  reading agents):
  [docs/trading_corpus_synthesis.md](docs/trading_corpus_synthesis.md) —
  evidence tiers, mechanism bank, 25 hypothesis families, documented nulls.
  Verdict: sharpens but does not reorder the agreed (unrecorded) 1–4
  ungating plan; MVP seed = momentum / short-horizon reversal / vol-gating
  families on a delisting-aware daily equity-ETF panel. Awaiting further
  information batches; ungating recorded only on the user's
  end-of-information signal.
- 2026-07-21 — **Information batch 3 ingested** (AI/ML shelf,
  verify-and-extract, four agents):
  [docs/ml_shelf_integration.md](docs/ml_shelf_integration.md). The playbook
  map passed its second independent audit; the pass caught and we **fixed an
  anti-conservative defect in the deflated-Sharpe promotion gate**
  (cross-trial variance benchmark + raw-kurtosis guard + ledger wiring) and
  hardened the trajectory-judge (identity pinning, bias battery, calibration
  authority limits). Suite: **170 tests green, deterministic**. Follow-on
  build items catalogued (integration doc §3). Not yet committed.

## Next recommended action

- **Decisions made (2026-07-22): 1–4 ungating recorded; first research phase
  authorized.** Both authorizations were given by the user in-session; the
  approved-decisions ledger records them. The Robinhood execution build remains
  gated behind a *validated survivor* (edge-first) and may never be built if
  nothing survives — that is the intended, money-saving outcome.
- **In progress — verifier hardening (research phase 1):** lead with the
  known-bad specimen fixtures (prove the harness rejects batch-6's junk before any
  pass is trusted — fail-before/pass-after), the calibration/ECE axis (S26), and
  the leakage-detector GAPS (S6 intra-bar, S7 non-causal decomposition, S8
  non-causal feature construction), plus the persistence/cost/DSR gates and S1
  forward-tracking. maker ≠ checker on every new gate; research-skeptic red-teams
  each. See `tasks/todo.md` → "research phase 1".
- **Then:** read-only Tiingo + FRED adapters into a point-in-time cache
  (delisting-aware equity/ETF panel) → cached MVP screen (H1–H3 seeds; consider
  leading with H3/volatility, the best-evidenced seed).
- **Still gated:** any Robinhood data or execution path, ML/forecasting, options.
  Execution is reached only after a strategy clears the full verification stack.
