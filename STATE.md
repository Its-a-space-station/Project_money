# STATE.md — Project_money

> A living snapshot of this project. Update it whenever the phase, scope, or
> constraints change — it is the first thing a new session reads after `CLAUDE.md`.
> Not executable automation.

*Last updated: 2026-07-20.*

## Phase

**Bootstrap — documentation only.** Project_money has adopted the Decision Systems
Playbook (tailored bootstrap): governance docs, canonical schemas, templates,
checklists, and a project blueprint are in place, and the quant-research
philosophy is merged into `CLAUDE.md`. **No implementation code, no provider
adapters, no broker integration exists or is permitted yet.**

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

## Safety rules (in force)

- Research-only; no autonomous financial actions (this system does not
  buy/sell/trade/order or move funds).
- **Robinhood is read-only, gated, and treated as a broker** — no execution path.
- Human approval required before any outward-facing or irreversible step.
- No secrets or credentials in the repo.
- Canonical labels only (see [docs/label_policy.md](docs/label_policy.md)).

## Non-goals

- No implementation code, provider/broker adapters, or execution paths (bootstrap).
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
  Project_money (no sibling-system references remain).

## Next recommended action

- Define the first deterministic MVP research slice for a single object type
  (e.g., `equity`) on cached data (requires user authorization to leave bootstrap).
