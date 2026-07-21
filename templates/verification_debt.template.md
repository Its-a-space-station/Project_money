# Verification Debt — {{PROJECT_NAME}}

> **Template.** A ledger of what is asserted-but-not-fully-verified, kept visible
> and bounded (mirrors `schemas/verification_debt.schema.json`). Research-only.
> Outstanding high-risk debt blocks promotion. Not executable automation.

- **Report id:** {{REPORT_ID}}
- **Project:** `{{PROJECT_SLUG}}`
- **Date:** {{DATE}}

## Verified items

Independently verified this cycle (maker ≠ checker).

- {{VERIFIED_ITEM}}

## Unverified assumptions

- {{UNVERIFIED_ASSUMPTION}} — risk: {{RISK_LEVEL}} (low / medium / high)

## Missing tests

- {{MISSING_TEST}}

## Bias risks

- Lookahead: {{LOOKAHEAD_RISK}}
- Survivorship: {{SURVIVORSHIP_RISK}}

## Config drift

- {{CONFIG_DRIFT_RISK}} (thresholds / criteria changed without re-validation).

## Overconfidence risk

- {{OVERCONFIDENCE_RISK}} (confidence exceeding what evidence supports).

## Promotion blockers

- {{PROMOTION_BLOCKER}}

## Next verifications (risk-ordered)

1. {{NEXT_VERIFICATION_1}}
2. {{NEXT_VERIFICATION_2}}
