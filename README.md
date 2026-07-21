# Project_money

A **research-only** quantitative decision-support system: it discovers, tests, and
continuously improves systematic investment strategies with a statistically
defensible edge, and turns observations into **verified, labeled findings and
human-readable reports**. It informs a human decision — it does not make the
decision and it does not act on it.

This repository currently holds **documentation, policies, schemas, templates, and
blueprints** — not implementation code. It is bootstrapped from the shared
[Decision Systems Playbook](../decision_systems_playbook/) and inherits its
architecture, safety posture, and verification discipline.

## Posture

| Aspect | Current state |
| --- | --- |
| Phase | Bootstrap — documentation only |
| Financial actions | **None.** Never buys, sells, trades, places orders, or moves funds |
| Data sources | Tiingo, FRED, Robinhood — **all read-only** (Robinhood is a gated broker) |
| Code / adapters | None yet (by design) |

See [docs/safety_policy.md](docs/safety_policy.md) for the hard constraints.

## How to read this repo

Start here, in sequence:

1. [CLAUDE.md](CLAUDE.md) — operating rules **and** the quant-research philosophy.
2. [STATE.md](STATE.md) — current phase, MVP scope, decisions, blockers.
3. [docs/architecture.md](docs/architecture.md) — the shared system model.
4. [docs/safety_policy.md](docs/safety_policy.md) — the hard constraints.
5. [docs/verification_policy.md](docs/verification_policy.md) — how claims earn trust.

Then the supporting policies in [docs/](docs/), the data shapes in
[schemas/](schemas/), scaffolding in [templates/](templates/), operational
[checklists/](checklists/), and the per-project plan in
[project_blueprints/](project_blueprints/).

## Repository layout

```text
README.md                 You are here
CLAUDE.md                 Operating rules + quant-research philosophy (merged)
AGENTS.md                 Codex entry point (points to CLAUDE.md)
STATE.md                  Current state of this project
tasks/                    Working backlog (todo.md) and accumulated lessons
docs/                     Architecture + governance policies (from the playbook)
schemas/                  Canonical data shapes (project = project_money)
templates/                Reusable report / record scaffolding
checklists/               Operational checklists
project_blueprints/       This project's design plan
```

## Relationship to the playbook

Project_money adopted a **tailored** slice of the playbook: the core governance
docs, the six canonical schemas, and lean templates/checklists. The playbook's
**v2 / v2.1 / v2.2** layers (engineering discipline, forecasting, macro /
market-structure) were **not** copied — they live in the shared playbook and can be
adopted later if that work is authorized. This repo remains independently
auditable; the playbook does not centrally control it.

## Status

Bootstrap phase. Documentation only. No code modules, no provider adapters, no
broker integrations. See [STATE.md](STATE.md) for the live status.
