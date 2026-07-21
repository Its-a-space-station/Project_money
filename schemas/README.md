# schemas/

Canonical data shapes for **Project_money**, adopted from the shared Decision
Systems Playbook. One concept, one shape — evidence, beliefs, decisions, reviews,
postmortems, and verification debt all speak the same language across the
research pipeline. The `project` enum is set to `project_money`; `object_type`
covers this project's multi-asset scope (equity, etf, option, macro_signal,
factor, other).

All schemas are **JSON Schema draft 2020-12** and describe **research-only**
objects: none of them authorize, recommend, or trigger any financial action.

## Status

**Initial schema set present (v1.0.0).** Six canonical object schemas exist.
Still documentation/schema-only — no code, providers, brokers, or scripts.

## The objects (suggested reading order)

Read in pipeline order — each builds on the one before it:

1. **[evidence_record.schema.json](evidence_record.schema.json)** — a single
   provenance-stamped observation from a provider (source, freshness,
   reliability, independence, extracted claims). The raw input to everything else.
2. **[belief_card.schema.json](belief_card.schema.json)** — a research thesis
   about one object, weighing evidence for/against, with uncertainty flags,
   confidence, validation status, and a research `decision_label`.
3. **[decision_card.schema.json](decision_card.schema.json)** — a gated
   research/triage decision on a BeliefCard: deterministic checks, optional AI
   and human review, and a mandatory `prohibited_actions_confirmed` safety
   attestation.
4. **[manual_review.schema.json](manual_review.schema.json)** — a human-in-the-
   loop review record (questions, reviewer decision, follow-up tasks).
5. **[postmortem.schema.json](postmortem.schema.json)** — a retrospective on a
   thesis once its outcome is known; emits lesson candidates and config
   proposals.
6. **[verification_debt.schema.json](verification_debt.schema.json)** — a
   per-project ledger of unverified assumptions and risks that gates promotion.

## Conventions

- `$schema` is draft 2020-12; every file carries a `$id` and a `schema_version`
  (`const "1.0.0"` for this set — bump the const when a shape changes).
- Field names are `snake_case`; objects set `"additionalProperties": false` to
  keep the canonical shape tight.
- Timestamps are RFC 3339 `date-time`; `created_at` is required, `updated_at`
  optional, on stateful records.
- **Approved research labels only** for decision/triage fields:
  `reject`, `watchlist`, `trigger_ready_research_candidate`,
  `needs_human_review`, `paper_candidate`, `research_only`, `validation_pending`.
  Action words (buy/sell/trade/order/entry/exit/recommendation) appear **only**
  inside `description` text as explicit prohibitions
  (see [../docs/label_policy.md](../docs/label_policy.md),
  [../docs/safety_policy.md](../docs/safety_policy.md)).
- No secrets, credentials, or personal financial account data in any schema or
  example.

## Cross-references

Provenance & freshness: [../docs/verification_policy.md](../docs/verification_policy.md)
· Labels: [../docs/label_policy.md](../docs/label_policy.md) ·
Safety: [../docs/safety_policy.md](../docs/safety_policy.md) ·
Debt: [../docs/verification_debt_policy.md](../docs/verification_debt_policy.md) ·
Promotion: [../docs/promotion_policy.md](../docs/promotion_policy.md)
