# Todo — {{PROJECT_NAME}}

> **Template.** Copy into the {{PROJECT_NAME}} repo as `tasks/todo.md`.
> Conventions: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked /
> needs decision. Nothing here authorizes leaving the current phase.

## Bootstrap docs

- [ ] Copy & adapt `CLAUDE.md`, `STATE.md`, `tasks/todo.md`, `tasks/lessons.md`
      from the playbook templates.
- [ ] Confirm the inherited safety, label, and verification policies apply.

## Schema adoption

- [ ] Adopt the canonical `schemas/` (evidence_record, belief_card,
      decision_card, manual_review, postmortem, verification_debt).
- [ ] Map {{PROJECT_NAME}} objects onto the `object_type` / `project` enums.

## Deterministic MVP

- [ ] Define deterministic, reproducible criteria for {{OBJECT_TYPE}}.
- [ ] Maker step produces candidates; checker step verifies independently.
- [ ] Assign canonical labels only: `reject`, `watchlist`,
      `trigger_ready_research_candidate`, `needs_human_review`, `paper_candidate`,
      `research_only`, `validation_pending`.

## Reports

- [ ] Daily report from `daily_report.template.md` (research-only warning + footer).
- [ ] Weekly report from `weekly_report.template.md`.

## Manual review

- [ ] Route `needs_human_review` / conflicting items via `manual_review.template.md`.
- [ ] Record reviewer decisions and follow-up tasks.

## Calibration

- [ ] Track outcomes; write postmortems for resolved theses.
- [ ] Review false positives / false negatives; propose config changes
      (proposals require human approval).

## Future integrations (gated — not authorized by this list)

- [!] Additional read-only providers (respect terms & rate limits).
- [!] Broker (e.g. Robinhood) read-only data — gated, no execution path; see
      `docs/broker_strategy.md`.
