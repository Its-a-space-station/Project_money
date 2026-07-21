# Verification Debt Policy

What we owe when something is asserted-but-not-fully-checked, or surfaced-but-
unverifiable. Verification debt makes coverage gaps **visible and bounded**
instead of silent. It is the counterpart to
[verification_policy.md](verification_policy.md).

## 1. Definition

**Verification debt** is any gap between what a finding claims and what has been
independently verified, that we have chosen to carry forward rather than resolve
immediately. Examples:

- A candidate could not be checked against a second source this run.
- A provider was rate-limited, so freshness could not be confirmed.
- Criteria changed and prior findings have not been re-derived.
- A schema or doc was adopted without an independent review pass.

Debt is **acceptable in the short term** and **dangerous when invisible or
unbounded**. The policy keeps it tracked and paid down.

## 2. Recording debt

Every debt item records:

- **What** is unverified (the specific claim or coverage gap).
- **Why** (rate limit, missing source, deferred review, etc.).
- **Risk** if it stays unverified (low / medium / high).
- **Created-at** and the run/loop that incurred it.
- **Pay-down plan** (what check would clear it).

In the bootstrap phase, debt lives in [../tasks/todo.md](../tasks/todo.md)
(marked `[!]`) and is summarized in [../STATE.md](../STATE.md). Once systems run,
each report includes a verification-debt section
(see [report_policy.md](report_policy.md)).

## 3. Effect on labels and reports

- A finding carrying debt is at most `Provisional` (never `Verified`) until the
  debt is cleared (see [verification_policy.md](verification_policy.md)).
- Reports always disclose outstanding debt; debt is never hidden to make output
  look cleaner.

## 4. Thresholds and the loop

Loops track accumulated debt and treat it as a **stop condition**: when debt
(by count or by aggregate risk) exceeds a configured threshold, the loop
**halts and surfaces** rather than piling on more unverified findings. See
[loop_architecture.md](loop_architecture.md).

## 5. Paying it down

- Each item has a concrete pay-down step; "verify later" is not a plan.
- Prioritize by risk: high-risk debt is cleared or escalated before new work.
- Clearing debt means an **independent** check succeeded (maker ≠ checker,
  [maker_checker_policy.md](maker_checker_policy.md)), not merely re-asserting.
- High-risk debt that cannot be cleared is escalated to a human.

## 6. Interaction with promotion

Outstanding high-risk debt blocks promotion to **Operational**
(see [promotion_policy.md](promotion_policy.md)). You cannot run a loop into a
known, unbounded verification gap.

## 7. Anti-patterns

- Carrying debt without recording it (invisible debt).
- Letting debt grow without a threshold (unbounded debt).
- Clearing debt by lowering standards instead of doing the check.
- Re-labeling `Provisional` as `Verified` to "close" an item.

## 8. Cross-references

[verification_policy.md](verification_policy.md) ·
[maker_checker_policy.md](maker_checker_policy.md) ·
[loop_architecture.md](loop_architecture.md) ·
[report_policy.md](report_policy.md) · [promotion_policy.md](promotion_policy.md)
