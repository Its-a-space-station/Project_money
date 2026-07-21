# STATE.md — {{PROJECT_NAME}}

> **Template.** Copy into the {{PROJECT_NAME}} repo and replace every
> `{{PLACEHOLDER}}`. Keep this current — it is the live snapshot a new session
> reads first. Not executable automation.

*Last updated: {{DATE}}.*

## Phase

**{{PROJECT_PHASE}}.** {{PHASE_DESCRIPTION}}

## Current MVP scope

- In scope: {{MVP_IN_SCOPE}}
- Explicitly deferred: {{MVP_DEFERRED}}

## Approved decisions

- {{DATE}} — {{APPROVED_DECISION}}

## Safety rules (in force)

- Research-only; no autonomous financial actions (this system does not
  buy/sell/trade/order or move funds).
- Human approval required before any outward-facing or irreversible step.
- No secrets or credentials in the repo.
- Canonical labels only (see playbook `label_policy.md`).

## Non-goals

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

## Active loops

Loops produce findings and reports only — never actions.

| Loop | Cadence | Bounds / stop conditions | Status |
| --- | --- | --- | --- |
| {{LOOP_NAME}} | {{CADENCE}} | {{STOP_CONDITIONS}} | {{LOOP_STATUS}} |

## Blockers

- {{BLOCKER}}

## Last checkpoint

- {{DATE}} — {{LAST_CHECKPOINT}}

## Next recommended action

- {{NEXT_ACTION}} (requires user authorization if it changes scope).
