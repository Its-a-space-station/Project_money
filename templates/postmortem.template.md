# Postmortem — {{PROJECT_NAME}}

> **Template.** Retrospective on a research thesis after its outcome is known
> (mirrors `schemas/postmortem.schema.json`). Research-only: it evaluates past
> research quality and does not authorize or trigger any financial action.

- **Postmortem id:** {{POSTMORTEM_ID}}
- **Object id:** {{OBJECT_ID}} (`{{OBJECT_TYPE}}`)
- **Original belief card id:** {{BELIEF_CARD_ID}}
- **Project:** `{{PROJECT_SLUG}}`
- **Date:** {{DATE}}

## Original belief

{{ORIGINAL_THESIS_SUMMARY}}

Original label: `{{ORIGINAL_DECISION_LABEL}}` · confidence: {{ORIGINAL_CONFIDENCE}}

## Outcome

**Outcome label:** {{OUTCOME_LABEL}} (`validated`, `invalidated`,
`partially_validated`, `inconclusive`, `false_positive`, `false_negative`).

{{OUTCOME_SUMMARY}}

## What worked

- {{WHAT_WORKED}}

## What failed

- {{WHAT_FAILED}}
- False-positive reason (if any): {{FALSE_POSITIVE_REASON}}
- False-negative reason (if any): {{FALSE_NEGATIVE_REASON}}

## Lesson candidates

Promote durable ones into `tasks/lessons.md`.

- {{LESSON_CANDIDATE_1}}
- {{LESSON_CANDIDATE_2}}

## Config change proposals

Proposals only — each requires human approval and the relevant promotion gate.

- {{CONFIG_CHANGE}} — rationale: {{RATIONALE}}

## Promotion / deprecation recommendation

**Recommendation:** {{PROMOTION_RECOMMENDATION}} (`promote`, `keep`, `demote`,
`deprecate`, `no_change`, `needs_human_review`).

A recommendation only — promotion requires its own gate and explicit human
authorization (see playbook `promotion_policy.md`).
