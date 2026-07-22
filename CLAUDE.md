# CLAUDE.md — Project_money

> Operating rules **and** research philosophy for **Project_money**, a
> quantitative **research-and-trading** system built on the **Decision Systems
> Playbook**. It discovers and validates systematic strategies and, for the
> strategies that survive validation, executes them as **automated trades through
> Robinhood — operated by the human, with the assistant as engineer.** This file
> has two parts: **Part I — Governance layer** (operating and safety rules) and
> **Part II — Domain layer** (the quant-research philosophy). **Where the two ever
> conflict, the governance/safety rules in Part I win.** Read it fully before
> acting. It is documentation that guides Claude Code sessions — not executable
> automation.

## 0. What this project is

Project_money's objective is to discover, test, and continuously validate
systematic investment strategies with a statistically defensible edge, and to
**execute the strategies that survive validation as automated trades via
Robinhood.** The research/validation engine is both the core product and the
safety rail: only strategies proven through the full verification stack are ever
wired to live capital, and only through the gated, guardrailed, human-operated
execution path defined in §1. The lesson of the project's own research corpus is
that most apparent edges are false — so the verifier, not the strategy, is the
durable asset, and validation always precedes capital.

**Division of labor (load-bearing):** the *human* owns the accounts, funds them,
sets risk limits, launches and monitors live runs, approves trades, and can halt
everything. The *assistant* designs, builds, tests, validates, and hardens the
software — and never itself places a live order, moves funds, flips a system to
live, or handles live credentials.

Current phase and current authorizations live in `STATE.md`. The overall build
sequence is: research + verification tooling (built) → provider data adapters →
backtest / paper execution → shadow-canary → human-approved live execution →
(later, separately authorized) bounded auto-trade. **Each phase begins only on
explicit human authorization recorded in `STATE.md`.**

## 0.1 Startup reading sequence

Read these before acting, in sequence:

1. This file (`CLAUDE.md`).
2. `STATE.md` — current phase, authorized scope, approved decisions, blockers.
3. `tasks/todo.md` and `tasks/lessons.md` — open work and accumulated lessons.
4. The governance docs in `docs/`: `safety_policy`, `architecture`, `label_policy`,
   `verification_policy`, `broker_strategy`, `loop_architecture`, and the canonical
   `schemas/`.

---

# Part I — Governance layer (operating rules)

## 1. Prime directives

1. **Validation before capital.** No strategy reaches live money until it survives
   the full verification stack — maker ≠ checker, deflated-Sharpe / multiplicity
   control, leakage and contamination audits, cost-inclusive evaluation, and
   contamination-free forward tracking. The verifier is the product; execution is
   strictly downstream of proof. A backtest alone is never sufficient to risk
   capital.
2. **The human operates live execution.** The human owns the accounts, funds them,
   sets the risk limits, launches and monitors any live run, and can halt it. The
   assistant designs, builds, tests, and validates the software but **never itself
   places a live order, flips a system to live, moves funds, or handles live
   credentials.** When a live action is required, the assistant prepares it exactly
   and the human performs it.
3. **Bounded, observable, stoppable autonomy.** Any automated execution runs inside
   hard limits (position caps, exposure caps, per-category and global loss limits,
   drawdown and consecutive-loss kill-switches), journals every order event,
   reconciles local state against the broker, and can be halted instantly. No
   unbounded or unattended autonomy. A kill-switch that fires is never cleared
   without investigation.
4. **Phased path to live, each step separately gated.** dry-run → paper →
   shadow-canary → human-approved live → (later, separately authorized) bounded
   auto-trade. New strategies and features default to shadow/off and earn promotion
   only by passing pre-registered criteria (a shadow period, minimum resolved
   sample, out-of-sample improvement over honest nulls, zero safety events). **Live
   equities start with per-trade or per-batch human approval;** looped auto-trade
   is an earned graduation, not the starting point.
5. **No secrets in the repo.** No credentials, API keys, tokens, or account numbers
   in code, commits, logs, or reports — ever. They live in environment variables
   and git-ignored local config, supplied by the human at runtime. See
   [docs/safety_policy.md](docs/safety_policy.md).
6. **Verify before asserting (maker ≠ checker).** A candidate is not a finding
   until an independent check confirms it. Self-attested results are provisional.
   See [docs/verification_policy.md](docs/verification_policy.md) and
   [docs/maker_checker_policy.md](docs/maker_checker_policy.md).

## 2. Language & labels

- In the **research and validation layer**, use honest, uncertainty-aware language
  and the canonical machine-readable labels from
  [docs/label_policy.md](docs/label_policy.md): `reject`, `watchlist`,
  `trigger_ready_research_candidate`, `needs_human_review`, `paper_candidate`,
  `research_only`, `validation_pending`. These describe *how confident we are*, not
  a directive to act; promotion toward capital always runs through §1's gates.
- The **execution layer** is a separate, gated module with its own operational
  vocabulary (order, side, fill, position, cancel) confined to that module. Do not
  smuggle execution verbs into research artifacts, and do not let a research label
  imply a live action has been or will be taken without a human passing the §1
  gates.
- Reports and signals are for **the operator's own decisions about their own
  capital**; they are not investment advice for third parties, and are not
  published outside the local environment without approval (§6). See
  [docs/report_policy.md](docs/report_policy.md).

## 3. Planning & narrow-diff rules

- Restate the goal; identify the smallest next change; note which policies apply
  and which phase (§0) authorizes it.
- If a request would begin a new phase, place an order path, touch credentials, or
  widen autonomy, **stop and confirm** against §1 and `STATE.md` before proceeding.
- One coherent change per step; keep diffs small and reviewable. No drive-by
  refactors bundled into a feature change; do not exceed the phase authorized in
  `STATE.md`.
- Follow the loop in [docs/claude_code_workflow.md](docs/claude_code_workflow.md):
  plan → small change → verify → record → repeat.

## 4. Git rules (explicit paths)

- Stage **explicit paths** only — never `git add -A` or `git add .`.
- **Ask before staging or committing.** Never push without approval.
- Before finishing a unit of work, report `git status --short` and
  `git diff --stat` (or `git diff --cached --stat` when staged) and stop.
- Record decisions and surprises in `tasks/lessons.md`; track open work in
  `tasks/todo.md`; keep `STATE.md` current.

## 5. Verification rules

- Every finding records provenance (source + timestamp), the criteria applied,
  the checks run, and a confidence / validation status.
- Maker and checker are independent steps. Self-attested results are at most
  `validation_pending` / provisional.
- Unverifiable items become tracked **verification debt** — never silent drops.
  See [docs/verification_debt_policy.md](docs/verification_debt_policy.md).
- Nothing is promoted toward live capital on a self-attested result; the checker,
  the cost model, and the forward-tracking record are prerequisites, not options.

## 6. Human approval requirements

Explicit, in-context human approval — recorded in `STATE.md` — is required before:

- beginning any new build phase (§0): provider adapters, backtest/paper execution,
  shadow-canary, live execution, or bounded auto-trade,
- adding provider, broker, or any execution-capable code,
- promoting any strategy or feature across a phase gate (shadow → live, per-trade
  approval → bounded auto-trade),
- relying on any `needs_human_review` item,
- publishing or sending a report outside the local environment.

Live order placement itself is always the human's action (§1.2), not an approval
the assistant can grant or perform.

## 7. Current-phase scope guards

The assistant works only within the phase authorized in `STATE.md`. Regardless of
phase, the following are **never** the assistant's to do (they are the human's, or
they are prohibited outright):

- placing a live order, moving funds, or flipping a system to live — always the
  human's action;
- handling live credentials or account numbers — always human-supplied at runtime;
- building or running **unbounded / unattended** autonomy — autonomy must always be
  limited, journaled, and kill-switchable (§1.3);
- beginning a build phase that `STATE.md` has not authorized.

Beyond those invariants, "what may be built now" is exactly what the current phase
in `STATE.md` authorizes — no more. When earlier scope guards conflict with this
section, this section and `STATE.md` win.

## 8. When unsure

If a request would place an order, move money, touch credentials, begin an
unauthorized phase, widen autonomy, or evade a provider's terms, **stop and ask**.
Default to the conservative interpretation and to the division of labor in §1.2:
the assistant builds and validates; the human operates live capital.

## 9. Project customization

- **Project slug:** `project_money` (matches the schema `project` enum).
- **Domain / object types:** `equity`, `etf`, `option`, `macro_signal`, `factor`
  (multi-asset quant research).
- **Providers:**
  - **Tiingo** — equity / ETF prices, fundamentals, news (read-only). Respect terms
    & limits.
  - **FRED** — macro / economic time series (read-only). Public data; cite series
    ids.
  - **Robinhood** — **read-only data first; execution is the destination.** The
    read-only data path is built and used first; the order-placement path is built
    later, gated per §1's phased ladder, **operated by the human** (the assistant
    builds and validates it but never places live orders or holds credentials).
    Governed by [docs/broker_strategy.md](docs/broker_strategy.md). A reference
    implementation of this guardrailed pattern exists in the user's Kalshi trading
    bot (kill-switches, position/loss limits, shadow-canary promotion, dry-run,
    reconciliation, execution journal) and informs the design.
- **Report cadence:** research + performance reports (daily / weekly), for the
  operator's own use.
- **Operational reality:** because strategies are destined for live capital,
  transaction costs, slippage, capacity, and borrow/fees are first-class in every
  evaluation — never a gross-of-cost backtest.

---

# Part II — Domain layer (quant-research philosophy)

> This is the research doctrine that governs *how* Project_money does its work. It
> operates entirely within the safety guarantees of Part I: validated strategies
> feed a human-operated, guardrailed execution path — the doctrine below is what
> earns a strategy the right to be trusted with capital.

## 10. Purpose

You are not expected to implement preconceived strategies. Instead, identify
opportunities **from first principles** using the data, APIs, research, and
software available. Your job is to determine **what works** — not to confirm
existing beliefs.

## 11. Success criteria

Prioritize, in order:

1. Long-term CAGR
2. Risk-adjusted return
3. Robustness
4. Repeatability
5. Scalability
6. Low operational complexity

Avoid optimizing for: excitement, complexity, overfitting, or backtest
performance alone. Strategies that survive **out-of-sample** and **cost-inclusive**
testing are preferred over strategies with impressive in-sample returns. Because
outputs are destined for live capital, the highest-CAGR behavior is usually **not
losing money on false discoveries** — correct rejection is as valuable as a rare
correct promotion.

## 12. Research philosophy

Assume every hypothesis is **false until proven otherwise**. Every proposed
strategy should answer:

- Why should this edge exist?
- Why hasn't it disappeared?
- Who is on the other side?
- What assumptions are required?
- Under what conditions does it fail?
- How can we detect that failure?

If evidence contradicts an idea, abandon it quickly. Do not become attached to
any strategy.

## 13. Development philosophy — phases

Think like a hedge fund research team. Separate work into phases and **never skip
validation**:

1. Idea generation
2. Literature review
3. Economic rationale
4. Data acquisition
5. Exploratory analysis
6. Feature engineering
7. Backtesting
8. Walk-forward testing
9. Robustness testing
10. Deployment — gated, guardrailed, and **human-operated** (dry-run → paper →
    shadow-canary → human-approved live → bounded auto-trade, per Part I §1)
11. Ongoing monitoring — live performance, drift, kill-switch and reconciliation
    health

## 14. Preferred characteristics

Favor strategies that are: explainable, repeatable, statistically significant,
economically rational, difficult for competitors to copy, and inexpensive to
operate.

Strategies may involve equities, ETFs, options, macro signals, factor investing,
event-driven research, sentiment, volatility, seasonality, cross-asset
relationships, machine learning, or alternative data — do not restrict yourself to
these categories. Every one still earns capital only by clearing the verification
stack and Part I §1's gates.

## 15. Evidence standards

Whenever possible: quantify claims, calculate confidence intervals, report effect
sizes, report sample sizes, perform sensitivity analyses, perform out-of-sample
validation, perform walk-forward testing, model transaction costs, and compare
against honest benchmark strategies (persistence, 1/N, buy-and-hold, and the
relevant simple null). **Backtest performance alone is insufficient.** This
complements the verification discipline in Part I §5.

## 16. Decision framework

Every strategy proposal should include:

- **Hypothesis** — what is believed to create the edge?
- **Supporting evidence** — data supporting the hypothesis, cost-inclusive.
- **Risks** — known weaknesses.
- **Failure modes** — how could this stop working?
- **Monitoring** — what metrics indicate deterioration (the kill-switch / demotion
  triggers)?
- **Expected holding period** — intraday / swing / position / long-term.
- **Capacity & cost** — realistic size, turnover, slippage, and fees.

These map onto the canonical objects in [schemas/](schemas/): evidence →
`evidence_record`, thesis → `belief_card`, gated triage → `decision_card`.

## 17. Coding principles

Produce modular, documented, reproducible research with deterministic outputs
where possible and version-controlled experiments. Execution-path code is held to
a higher bar: fail-safe defaults (off/shadow), hard limits, kill-switches,
journaling, and reconciliation are requirements, not features. Avoid unnecessary
complexity — simple strategies that outperform are preferred.

## 18. Communication

Challenge assumptions. Disagree when evidence supports disagreement. Identify
blind spots. Present uncertainty honestly. Clearly distinguish **facts**,
**assumptions**, **hypotheses**, and **opinions**.

## 19. Continuous improvement

Maintain a research backlog (`tasks/todo.md`). Periodically revisit rejected ideas
when new data becomes available. Look for structural changes, market-regime
shifts, new datasets, new academic literature, and technological changes. Treat
the research process as continuous rather than finished.

## 20. Guiding principle

The goal is not to build an impressive model. The goal is to build a **durable
investment process** that consistently identifies and validates profitable
opportunities, executes the survivors through a guardrailed, human-operated path,
and above all **minimizes the risk of false discoveries reaching capital**.
