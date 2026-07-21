# Architecture

The shared system model that every decision system in this playbook inherits.
This is the mental model; the policies in the sibling docs make it concrete.

## 1. What a "decision system" is here

A **decision system** is a research pipeline that turns raw observations from
the outside world into **verified, labeled findings and human-readable reports**.
It informs a human decision. It does not make the decision and it does not act
on it. Project_money — across its equities, ETFs, options, macro, and factor
research — is an instance of this shape: every strategy or screen it runs is a
pipeline of this form.

## 2. The canonical pipeline

```text
   Sources                Pipeline stages                     Output
  ─────────   ───────────────────────────────────────────   ────────
  providers → INGEST → NORMALIZE → ANALYZE → VERIFY → REPORT → human
   (data)      raw      schema-    candidate  checker  labeled   reviews
              capture   shaped     findings   review   report    & decides
```

- **Ingest** — pull raw data from providers behind a stable interface. No
  business logic here. See [provider_strategy.md](provider_strategy.md).
- **Normalize** — coerce raw data into canonical schemas (see
  [../schemas/](../schemas/)). One shape per concept, shared across systems.
- **Analyze** — apply the system's criteria to produce *candidate* findings.
  This is the **maker** role.
- **Verify** — an independent step checks each candidate against its source and
  the verification rules. This is the **checker** role. See
  [verification_policy.md](verification_policy.md) and
  [maker_checker_policy.md](maker_checker_policy.md).
- **Report** — emit labeled, disclaimer-bearing output for a human. See
  [report_policy.md](report_policy.md).

A finding that fails verification is not dropped silently — it is recorded as
verification debt (see [verification_debt_policy.md](verification_debt_policy.md))
or downgraded in confidence, never quietly promoted.

## 3. Layering

```text
┌─────────────────────────────────────────────┐
│ Reporting layer   reports, disclaimers       │  read-only to humans
├─────────────────────────────────────────────┤
│ Decision-support  criteria, scoring, labels  │  research-only logic
├─────────────────────────────────────────────┤
│ Verification      maker/checker, confidence  │  independent of analysis
├─────────────────────────────────────────────┤
│ Normalization     canonical schemas          │  shared across systems
├─────────────────────────────────────────────┤
│ Provider layer    data adapters (abstract)   │  swappable, rate-limited
└─────────────────────────────────────────────┘
```

Rules of the layering:

- Each layer depends only on the layer below it through a defined contract.
- The provider layer is **abstract** — no system codes against a concrete vendor
  API; it codes against the provider interface. (No adapters exist yet.)
- A **broker** (here, Robinhood) is a *read-only data provider* in this
  architecture until and unless a future, separately-authorized phase changes
  that. It is never an action sink. See [broker_strategy.md](broker_strategy.md).

## 4. Control flow: loops, not one-shots

Systems run as bounded, observable **loops** rather than long autonomous runs.
The loop architecture (cadence, guards, stop conditions, idempotency) is defined
in [loop_architecture.md](loop_architecture.md). Loops are designed so a human
can inspect, pause, and resume them, and so re-running is safe.

## 5. Shared vs. per-system

| Shared (this playbook) | Per-system (downstream repos) |
| --- | --- |
| Pipeline shape, layering | Concrete criteria and thresholds |
| Canonical schemas | Provider choices and adapters |
| Safety, verification, label, report policy | Domain-specific scoring |
| Loop + maker/checker structure | Storage, scheduling, deployment |
| Promotion + debt policy | Implementation code and tests |

## 6. Non-goals

- No autonomous financial action of any kind.
- No order placement, fund movement, or position changes.
- No vendor lock-in baked into the shared layer.
- No secrets, credentials, or personal financial data in any repo.

## 7. Cross-references

Safety: [safety_policy.md](safety_policy.md) ·
Workflow: [claude_code_workflow.md](claude_code_workflow.md) ·
Loops: [loop_architecture.md](loop_architecture.md) ·
Verification: [verification_policy.md](verification_policy.md) ·
Maker/checker: [maker_checker_policy.md](maker_checker_policy.md) ·
Labels: [label_policy.md](label_policy.md) ·
Reports: [report_policy.md](report_policy.md) ·
Providers: [provider_strategy.md](provider_strategy.md) ·
Brokers: [broker_strategy.md](broker_strategy.md) ·
Promotion: [promotion_policy.md](promotion_policy.md) ·
Debt: [verification_debt_policy.md](verification_debt_policy.md)
