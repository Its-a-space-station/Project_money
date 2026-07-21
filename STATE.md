# STATE.md — Project_money

> A living snapshot of this project. Update it whenever the phase, scope, or
> constraints change — it is the first thing a new session reads after `CLAUDE.md`.
> Not executable automation.

*Last updated: 2026-07-20.*

## Phase

**Tooling build (research-tooling code authorized 2026-07-20).** The playbook
bootstrap is complete and the first tooling code exists under `src/project_money/`
with a green deterministic test suite (`tests/`, 81 tests): verification backbone
(invariants incl. lookahead detector, metrics + deflated Sharpe, walk-forward,
prequential codelength, evaluation cascade), leakage/vintage auditor,
metric-falsification harness, hypothesis ledger + tabu memory, MDL complexity
gate. **Still no provider adapters, no broker integration, no execution paths —
those remain separately gated.**

## Current MVP scope

- **In scope (once authorized):** a deterministic, reproducible research slice on
  cached data — the smallest verifiable strategy screen with maker/checker
  separation and canonical labels, plus a research report.
- **Explicitly deferred:** any live data feed, provider adapters (Tiingo/FRED),
  broker access (Robinhood), machine-learning / forecasting models, options and
  cross-asset modeling.

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

## Safety rules (in force)

- Research-only; no autonomous financial actions (this system does not
  buy/sell/trade/order or move funds).
- **Robinhood is read-only, gated, and treated as a broker** — no execution path.
- Human approval required before any outward-facing or irreversible step.
- No secrets or credentials in the repo.
- Canonical labels only (see [docs/label_policy.md](docs/label_policy.md)).

## Non-goals

- No provider/data adapters, broker code, or execution paths (each separately
  gated; research-tooling code is the only authorized code).
- No autonomous financial action anywhere in scope.
- No v2 / v2.1 / v2.2 playbook layers (forecasting, macro, object-memory) adopted
  yet — they remain in the shared playbook and can be pulled in later if authorized.

## Active loops

None. Loops, when built, produce findings and reports only — never actions.

| Loop | Cadence | Bounds / stop conditions | Status |
| --- | --- | --- | --- |
| — | — | — | none |

## Blockers

- None. Next steps are gated on explicit user authorization, not blocked.

## Last checkpoint

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
  regression tests; **159 tests green, deterministic**. Deferred: TOOLMAKER-
  style build harness (admission gate only). Not yet committed.

## Next recommended action

- Define the first deterministic MVP research slice for a single object type
  (e.g., `equity`) on cached data (requires user authorization to leave bootstrap).
