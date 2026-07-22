# Report Policy

How findings and activity reach the operator. Reports are the system's primary
human-facing output. Research/validation reports inform; execution/performance
reports record what the operator's own system did.

## 1. Principles

- **For the operator's own use.** A research/validation report describes
  observations and confidence; a performance/execution report describes the
  operator's own live activity. Neither is investment advice for third parties.
- **Evidence-bearing.** Every finding cites its sources, timestamps, applied
  criteria, and confidence label. A reader can retrace it.
- **Honest about uncertainty.** Provisional, conflicting, and stale findings are
  shown as such — never laundered into apparent certainty.
- **Layer-appropriate vocabulary.** Research/validation reports use the approved
  research labels in [label_policy.md](label_policy.md) and avoid directive
  framing; execution/performance reports may state realized orders, fills, and
  positions as facts about what the operator's system did.

## 2. Required disclaimer

Every report begins with, verbatim or in close paraphrase:

> **For the operator's own use. Not third-party financial advice.** This report
> summarizes automated observations and/or the operator's own system activity for
> the operator's review. Any live action is taken by the operator through the
> guardrailed, human-operated execution path — not by this report.

## 3. Standard report structure

1. **Header** — system name, run/loop id, generated-at timestamp, data window.
2. **Disclaimer** — as in §2.
3. **Summary** — counts by result label and confidence label; what changed since
   last report.
4. **Findings** — each with: subject/identifier, result label, confidence label,
   key evidence, source + timestamp, and a plain-language note.
5. **Conflicts & escalations** — `Conflicting` (confidence) and
   `needs_human_review` (result) items for human adjudication, surfaced prominently.
6. **Verification debt** — what could not be verified this run, and why
   (see [verification_debt_policy.md](verification_debt_policy.md)).
7. **Operational notes** — provider health, rate-limit status, anomalies, loop
   metrics.

## 4. Labeling in reports

- Pair every finding's **result label** (what we saw) with its **confidence
  label** (how sure we are): e.g., `watchlist` / `provisional`.
- Sort or group so the highest-confidence, highest-interest items are easy to
  find, but never hide low-confidence items.

## 5. Distribution

- Reports are generated for human review. **Publishing or sending a report
  outside the local environment is an outward-facing action** and requires
  explicit, in-context approval (see [safety_policy.md](safety_policy.md)).
- Reports must not contain secrets, credentials, or personal financial account
  data. Redact identifiers that are not necessary for the research purpose.

## 6. Tone

Neutral, observational, and specific. State what was measured and how confident
we are. Avoid persuasive or directive language. The reader decides.

## 7. Status

No reporting layer is built yet. This is the contract a future reporting layer
must meet. Report types: research findings, validation results, and — once
execution is authorized — live-performance and safety-health reports (kill-switch
state, reconciliation, fill quality) for the operator.

## 8. Cross-references

[safety_policy.md](safety_policy.md) · [label_policy.md](label_policy.md) ·
[verification_policy.md](verification_policy.md) ·
[verification_debt_policy.md](verification_debt_policy.md) ·
[architecture.md](architecture.md)
