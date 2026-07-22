# Label Policy

The controlled vocabulary for describing results. Labels shape intent, so they
are governed. This complements the *confidence* labels in
[verification_policy.md](verification_policy.md): confidence says *how sure we
are*; result labels say *what we observed*.

## 1. Forbidden vocabulary in the research / validation layer

Do **not** use these as labels, field names, enum values, identifiers, file
names, or report terms **in the research / validation layer** (findings, belief
cards, decision cards, research and validation reports, and the canonical
schemas):

> **Buy · Sell · Trade · Order · Execute · Fill · Entry · Exit · Recommendation ·
> Position (as an action) · Long/Short (as a directive)**

In that layer they imply directives the research output must not carry. They are
permitted only inside safety negations, forbidden-label examples, or a schema
`description` that explicitly forbids them.

**The execution layer is exempt — and separate.** The gated execution module
(order placement, fills, positions, cancels) legitimately uses this operational
vocabulary *within that module*. The rule is not "these words never appear"; it is
"these words never leak into a research artifact or a canonical research label,"
so that a research state can never be mistaken for a live action taken. Crossing
from a research label to a live order always runs through the human-operated gates
in [safety_policy.md](safety_policy.md) §1/§4.

## 2. Approved result vocabulary (canonical)

The canonical labels are **machine-readable `lower_snake_case` strings** and are
the single source of truth shared with code and stored data. They match the
`decision_label` / `allowed_decision_label` / `reviewer_decision` enums in the
[../schemas/](../schemas/) **exactly** — change them only by editing this table
and the schema enums together. The display name is an **optional** human-readable
rendering with no authority of its own.

| Canonical label (use this) | Optional display name | Meaning (research framing) |
| --- | --- | --- |
| `reject` | Reject | Ruled out of research consideration; does not meet criteria. |
| `watchlist` | Watchlist | Notable; monitor, but not yet a research candidate. |
| `trigger_ready_research_candidate` | Trigger-Ready Research Candidate | Meets the system's criteria; ready for closer **research** (never action). |
| `needs_human_review` | Needs Human Review | Requires human adjudication before reliance (conflict, low confidence, near a boundary). |
| `paper_candidate` | Paper Candidate | Eligible for paper / simulated **research study only** — never live execution. |
| `research_only` | Research Only | Retained purely for research / learning; no further triage implied. |
| `validation_pending` | Validation Pending | Surfaced, but verification is incomplete; awaiting validation. |

These seven are the complete approved set. Do **not** introduce a new label
without updating this table **and** the schema enums in the same change.
Confidence / validation state is a *separate* axis — see
[verification_policy.md](verification_policy.md).

## 3. Per-domain framing (research layer)

Project_money is multi-asset; the same canonical labels apply to every object type.
Examples of approved framing vs. forbidden framing:

| Object domain | Example approved framing | Never |
| --- | --- | --- |
| Equities / ETFs | `trigger_ready_research_candidate`, `watchlist`, `needs_human_review` | "buy/sell signal" |
| Options | `research_only`, `needs_human_review`, `validation_pending` | "open this position", "entry/exit" |
| Macro signals | `watchlist`, `research_only` | "risk-on trade", "rotate into…" |
| Factor research | `trigger_ready_research_candidate`, `reject` | "long/short this factor" |
| Robinhood (research view) | `research_only`, `needs_human_review`, `paper_candidate` | an execution label on a *research* artifact (order/fill belong to the execution module, not here) |

## 4. Naming rules

- The **canonical, machine-readable** form is the `lower_snake_case` value in §2.
  Code, schemas, and stored records use exactly those strings — nothing else.
- **Display names are optional presentation only.** They must map 1:1 to a
  canonical value, carry no authority, and are never stored or branched on.
- One concept, one canonical label. Do not invent synonyms. Adding or renaming a
  label means editing §2 and the schema enums in the same change.
- Pair a result/decision label with a confidence/validation label on every
  finding (e.g., `watchlist` / `provisional`).

## 5. Why this matters

Vocabulary is a safety control. A *research* field named `buy_signal` invites
someone — or some automation — to treat an unvalidated observation as an
instruction. A field whose value is `watchlist` or `research_only` describes a
research state and leaves the decision with the human and the §1/§4 gates. Keeping
execution vocabulary confined to the gated execution module is what stops a
research state from silently becoming a live order.

## 6. Playbook v2 note

v2 does **not** change this vocabulary. The seven canonical labels in §2 and the
forbidden action words in §1 are unchanged; v2's new policies (verifiers, object
memory, evaluators) assign only these canonical labels and continue to treat
buy / sell / trade / order / entry / exit / recommendation as forbidden except in
safety negations, forbidden-label examples, or clearly qualified domain phrases.

## 7. Cross-references

[safety_policy.md](safety_policy.md) · [verification_policy.md](verification_policy.md)
· [report_policy.md](report_policy.md) · [architecture.md](architecture.md)
