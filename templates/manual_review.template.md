# Manual Review — {{PROJECT_NAME}}

> **Template.** Human-in-the-loop review record (mirrors
> `schemas/manual_review.schema.json`). Research-only: a review produces a
> research / triage judgement and follow-up tasks — it does not authorize or
> trigger any financial action.

- **Review id:** {{REVIEW_ID}}
- **Object id:** {{OBJECT_ID}} (`{{OBJECT_TYPE}}`)
- **Project:** `{{PROJECT_SLUG}}`
- **Reviewer:** {{REVIEWER}}
- **Date:** {{DATE}}

## Object summary

{{OBJECT_SUMMARY}}

## Reason for review

{{REASON_FOR_REVIEW}} (e.g., `needs_human_review` label, conflicting evidence,
low confidence, near a safety boundary).

## Key questions

- {{QUESTION_1}}
- {{QUESTION_2}}

## Evidence for

- {{EVIDENCE_FOR}} (evidence_id, source, timestamp)

## Evidence against

- {{EVIDENCE_AGAINST}} (evidence_id, source, timestamp)

## Reviewer decision

**Decision (canonical label):** `{{REVIEWER_DECISION}}`

Allowed values: `reject`, `watchlist`, `trigger_ready_research_candidate`,
`needs_human_review`, `paper_candidate`, `research_only`, `validation_pending`.
These are research / triage states only — none authorizes any financial action.

**Reviewer notes:** {{REVIEWER_NOTES}}

## Follow-up tasks

- [ ] {{FOLLOW_UP_TASK_1}}
- [ ] {{FOLLOW_UP_TASK_2}}
