# Daily Research Report — {{PROJECT_NAME}}

> **⚠️ Research only — not financial advice.** This report summarizes automated
> observations for human review. It does **not** recommend, initiate, or execute
> any financial action. It does not buy, sell, trade, place an order, or move
> funds. Verify independently before making any decision.

- **Project:** {{PROJECT_NAME}} (`{{PROJECT_SLUG}}`)
- **Date:** {{DATE}}
- **Run / loop id:** {{RUN_ID}}
- **Data window:** {{DATA_WINDOW}}

## Summary

{{SUMMARY}}

## Candidate counts

| Label | Count |
| --- | --- |
| `trigger_ready_research_candidate` | {{N_TRIGGER_READY}} |
| `watchlist` | {{N_WATCHLIST}} |
| `needs_human_review` | {{N_NEEDS_REVIEW}} |
| `paper_candidate` | {{N_PAPER_CANDIDATE}} |
| `research_only` | {{N_RESEARCH_ONLY}} |
| `validation_pending` | {{N_VALIDATION_PENDING}} |
| `reject` | {{N_REJECT}} |

## Trigger-ready research candidates

Meets the system's criteria; surfaced for closer **research** — not an action
signal.

| {{OBJECT_TYPE}} id | Confidence | Validation | Key evidence | Source / time |
| --- | --- | --- | --- | --- |
| {{OBJECT_ID}} | {{CONFIDENCE}} | {{VALIDATION_STATUS}} | {{EVIDENCE}} | {{SOURCE}} |

## Watchlist

Notable, not yet a candidate.

| {{OBJECT_TYPE}} id | Why watching | Missing criteria |
| --- | --- | --- |
| {{OBJECT_ID}} | {{REASON}} | {{MISSING_CRITERIA}} |

## Needs human review

Conflicting, low-confidence, or near a boundary — a human must adjudicate before
reliance.

| {{OBJECT_TYPE}} id | Reason | Question for reviewer |
| --- | --- | --- |
| {{OBJECT_ID}} | {{REASON}} | {{QUESTION}} |

## Reject summary

- Total `reject`: {{N_REJECT}}
- Top reasons: {{REJECT_REASONS}}

## Data quality warnings

- {{DATA_QUALITY_WARNING}} (e.g., stale data, rate-limit gaps, single-source,
  correlated sources).

## Verification summary

- Verified (independent check): {{N_VERIFIED}}
- `validation_pending`: {{N_VALIDATION_PENDING}}
- Conflicting / escalated: {{N_CONFLICTING}}
- New verification debt: {{N_DEBT}} (see the verification-debt report).

---

*Safety footer: research-only output from the {{PROJECT_NAME}} system. No
autonomous financial actions are taken or implied. Human review is required
before any decision. Generated per the Decision Systems Playbook.*
