# templates/

Reusable Markdown scaffolding for **Project_money**, adopted from the shared
Decision Systems Playbook — so every report and record starts safe, consistent,
and research-only.

These are **documentation templates, not executable automation.** Copy a file
into place, then replace every `{{PLACEHOLDER}}`.

## Status

**Lean template set present.** The report / record templates and the STATE / tasks
scaffolding were adopted. `CLAUDE.md` and `STATE.md` are already filled in at the
repo root (the quant-research philosophy is merged into `CLAUDE.md`, so the generic
CLAUDE template was not copied). The playbook's v2 / v2.1 / v2.2 record templates
(task-spec, verifier, forecasting, macro, etc.) were **not** copied — they live in
the shared playbook and can be adopted later.

## What's here (reading sequence)

Project scaffolding (the STATE / tasks templates the root files were built from):

1. **[STATE.template.md](STATE.template.md)** — live snapshot: phase, MVP scope,
   approved decisions, safety rules, non-goals, active loops, blockers, last
   checkpoint, next action.
2. **[tasks.todo.template.md](tasks.todo.template.md)** — backlog: bootstrap,
   schema adoption, deterministic MVP, reports, manual review, calibration,
   gated future integrations.
3. **[tasks.lessons.template.md](tasks.lessons.template.md)** — durable lessons:
   workflow, safety, project-specific, repeated mistakes.

Recurring outputs — copy per run / per object:

1. **[daily_report.template.md](daily_report.template.md)** — daily findings with
   research-only warning, candidate counts, review queue, data-quality and
   verification summaries, safety footer.
2. **[weekly_report.template.md](weekly_report.template.md)** — outcome review,
   false positives / negatives, calibration, approval-gated change proposals,
   verification-debt summary, safety footer.
3. **[manual_review.template.md](manual_review.template.md)** — human review
   record (mirrors `manual_review` schema).
4. **[postmortem.template.md](postmortem.template.md)** — thesis retrospective
   (mirrors `postmortem` schema).
5. **[verification_debt.template.md](verification_debt.template.md)** — debt
   ledger (mirrors `verification_debt` schema).

> The playbook's v2 / v2.1 / v2.2 record templates (task-spec, verification-report,
> verifier, object-graph, forecasting benchmark / leakage, macro stance,
> structural-break, etc.) were **not** adopted in this tailored bootstrap. If that
> work is later authorized, copy them from the shared playbook's `templates/`.

## Placeholder conventions

Replace `{{DOUBLE_BRACE}}` tokens on copy. Common ones:

| Placeholder | Meaning |
| --- | --- |
| `{{PROJECT_NAME}}` | Human name, e.g. "Project_money" |
| `{{PROJECT_SLUG}}` | Machine name matching the schema `project` enum, e.g. `project_money` |
| `{{PROJECT_PHASE}}` | e.g. Bootstrap, MVP, Calibration |
| `{{DATE}}` | ISO date `YYYY-MM-DD` |
| `{{OBJECT_ID}}` / `{{OBJECT_TYPE}}` | The studied object and its kind |
| `{{RUN_ID}}` / `{{REPORT_ID}}` / `{{REVIEW_ID}}` / `{{POSTMORTEM_ID}}` | Record ids |

## Rules

- Use only the canonical labels from [../docs/label_policy.md](../docs/label_policy.md):
  `reject`, `watchlist`, `trigger_ready_research_candidate`, `needs_human_review`,
  `paper_candidate`, `research_only`, `validation_pending`.
- Action words (buy / sell / trade / order / entry / exit / recommendation) appear
  **only** in safety negations or forbidden-label examples.
- Report templates carry a research-only warning and a safety footer
  (see [../docs/report_policy.md](../docs/report_policy.md)).
- Templates name human-review boundaries and verification sections explicitly.
- No secrets, credentials, or personal financial account data.

## Cross-references

Schemas these mirror: [../schemas/](../schemas/) ·
Labels: [../docs/label_policy.md](../docs/label_policy.md) ·
Reports: [../docs/report_policy.md](../docs/report_policy.md) ·
Safety: [../docs/safety_policy.md](../docs/safety_policy.md) ·
Workflow: [../docs/claude_code_workflow.md](../docs/claude_code_workflow.md)
