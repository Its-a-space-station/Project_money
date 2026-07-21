# Weekly Research Report — {{PROJECT_NAME}}

> **⚠️ Research only — not financial advice.** This report summarizes automated
> observations for human review. It does **not** recommend, initiate, or execute
> any financial action. It does not buy, sell, trade, place an order, or move
> funds. Verify independently before making any decision.

- **Project:** {{PROJECT_NAME}} (`{{PROJECT_SLUG}}`)
- **Week of:** {{WEEK_OF}} ({{WEEK_RANGE}})

## Weekly summary

{{WEEKLY_SUMMARY}}

## Outcome review

Outcome labels are evaluative: `validated`, `invalidated`, `partially_validated`,
`inconclusive`, `false_positive`, `false_negative`.

| Object id | Original label | Outcome | Notes |
| --- | --- | --- | --- |
| {{OBJECT_ID}} | {{ORIGINAL_LABEL}} | {{OUTCOME_LABEL}} | {{NOTES}} |

## False positives / false negatives

- False positives: {{N_FALSE_POSITIVE}} — {{FALSE_POSITIVE_NOTES}}
- False negatives: {{N_FALSE_NEGATIVE}} — {{FALSE_NEGATIVE_NOTES}}

## Calibration notes

- Confidence vs. observed outcome: {{CALIBRATION_SUMMARY}}
- Adjustments to consider: {{CALIBRATION_ADJUSTMENTS}}

## Suggested changes (require approval)

Proposals only — nothing here is applied without explicit human approval and the
relevant promotion gate.

- {{SUGGESTED_CHANGE}} — rationale: {{RATIONALE}}

## Verification debt summary

- Open debt items: {{N_DEBT_OPEN}}
- High-risk: {{N_DEBT_HIGH}}
- Promotion blockers: {{PROMOTION_BLOCKERS}}

---

*Safety footer: research-only output from the {{PROJECT_NAME}} system. No
autonomous financial actions are taken or implied. Human review is required
before any decision. Generated per the Decision Systems Playbook.*
