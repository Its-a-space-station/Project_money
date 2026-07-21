# Verification Policy

How a claim earns the right to be called a finding. Verification is a first-class
pipeline stage (see [architecture.md](architecture.md)), not an afterthought.

## 1. Principle

**Nothing is asserted that has not been checked against a source.** Analysis
produces *candidates*; verification turns candidates into *findings* with an
explicit confidence label. Unverified material is never silently promoted; it is
either downgraded or tracked as debt
(see [verification_debt_policy.md](verification_debt_policy.md)).

## 2. What must be verified

- **Source provenance** — the datum came from the provider it claims to, at a
  known time, through a known interface.
- **Freshness** — the data is within the acceptable age for its use; stale data
  is labeled stale.
- **Criteria application** — the system's rules were applied correctly to the
  data (recomputable from inputs).
- **Internal consistency** — derived values agree with their inputs; no
  contradictions across fields.
- **Reproducibility** — given the same inputs, the same candidate is produced.

## 3. Confidence labels

Every finding carries exactly one confidence label:

| Label | Meaning |
| --- | --- |
| `Verified` | Checked against source; criteria reproducibly satisfied. |
| `Provisional` | Plausible but one or more checks are incomplete. |
| `Unverified` | Surfaced for transparency; checks not yet done. |
| `Conflicting` | Sources or checks disagree; needs human adjudication. |
| `Stale` | Was verified, but the underlying data is now too old. |

Labels only move *downward* automatically (e.g., `Verified` → `Stale`). Moving a
label upward requires a fresh verification pass. These confidence labels are
distinct from the *result* labels in [label_policy.md](label_policy.md).

## 4. Maker / checker separation

The step that produced a candidate may not be the sole step that verifies it.
An independent checker re-derives or cross-checks the result. See
[maker_checker_policy.md](maker_checker_policy.md). Self-attested results without
an independent pass are at most `Provisional`.

In dynamic multi-agent workflows, **adversarial verification** — independent
skeptic agents that each try to refute a finding — is an encouraged technique for
high-stakes findings, provided the skeptics are independent of the maker and do
not replace a deterministic check where one exists.

## 5. Evidence trail

Each finding records: the source(s) and timestamps, the criteria/version
applied, the checks run and their outcomes, and the resulting confidence label.
A reviewer must be able to retrace the path from raw observation to finding.

## 6. Handling failure

- A failed check **downgrades** the label and records *why*.
- Findings that cannot be verified within policy are logged as **verification
  debt**, not dropped — so coverage gaps stay visible.
- A `Conflicting` finding is escalated to a human, never auto-resolved.

## 7. Verification in the bootstrap phase

There is no code yet, so "verification" currently means: documents are
internally consistent, cross-links resolve, and policies do not contradict one
another. As schemas and code arrive, this policy extends to data and tests.

## 8. Cross-references

[architecture.md](architecture.md) · [maker_checker_policy.md](maker_checker_policy.md)
· [label_policy.md](label_policy.md) · [report_policy.md](report_policy.md) ·
[verification_debt_policy.md](verification_debt_policy.md)
