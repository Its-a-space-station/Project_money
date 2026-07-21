# Checklist — Before a Paper Workflow

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask.

Run this before starting paper-only opportunity tracking. Paper means
**simulated, research-only** — there is no live external action.

## Prerequisites

- [ ] **Research-only reports exist** (with the research-only warning and safety
      footer).
- [ ] A **manual review process exists** for `needs_human_review` items.
- [ ] **Outcome labels are defined** (`validated`, `invalidated`,
      `partially_validated`, `inconclusive`, `false_positive`, `false_negative`).

## Honest modeling

- [ ] Friction / slippage / execution-cost assumptions are **documented and
      modeled for paper analysis only**, where applicable.
- [ ] Paper items are labeled `paper_candidate` and never escalated to a live
      capability.

## Safety & learning loop

- [ ] **No live external action** — the workflow is paper-only.
- [ ] A **postmortem path exists** (postmortem schema / template) for resolved
      items.
- [ ] A **verification-debt report exists** to track unverified assumptions.
