# Loop Architecture

Decision systems run as **bounded, observable loops**, not long autonomous runs.
This document defines how loops are structured so they stay safe, inspectable,
and re-runnable. It refines the pipeline in [architecture.md](architecture.md).

## 1. Why loops

A loop gives us natural checkpoints: between iterations a human can inspect,
pause, or stop, and the system can enforce guards. Long unattended runs hide
state and accumulate risk. Most loops here are **research / monitoring loops** — they end in findings and
reports, never in an action. A distinct **execution loop** exists only in the
gated live-trading phase (Phase 6, per [broker_strategy.md](broker_strategy.md)
§3): it places orders **only within hard limits + kill-switches, fully journaled,
and instantly haltable — human-operated, never unbounded or unattended, and never
launched or run by the assistant.** See [safety_policy.md](safety_policy.md).

## 2. Anatomy of one iteration

```text
        ┌──────────────────────────────────────────────┐
        │  WAKE  (cadence / trigger, within rate limit) │
        ├──────────────────────────────────────────────┤
        │  INGEST    pull raw data via provider iface   │
        │  NORMALIZE coerce to canonical schema         │
        │  ANALYZE   produce candidates  (maker)        │
        │  VERIFY    independent check   (checker)      │
        │  LABEL     result + confidence labels         │
        │  REPORT    persist / surface findings         │
        │  RECORD    metrics, debt, lessons             │
        ├──────────────────────────────────────────────┤
        │  CHECK STOP CONDITIONS → sleep or halt        │
        └──────────────────────────────────────────────┘
```

In a research / monitoring loop, no step places an order or moves money; its
outputs are data, findings, reports, and operational records. Order placement
lives only in the separate, gated, human-operated execution loop (§1).

## 3. Required properties

- **Idempotent.** Re-running an iteration over the same window must not create
  duplicate or contradictory findings. Use stable keys and upserts.
- **Bounded.** Each iteration has a max work size, a timeout, and a max number
  of provider calls. No unbounded fan-out.
- **Rate-limited.** Provider calls respect documented limits and back off on
  errors. See [provider_strategy.md](provider_strategy.md).
- **Observable.** Each iteration emits structured metrics (counts, latencies,
  error rates, debt added) a human can review.
- **Resumable.** State is checkpointed so a paused or crashed loop resumes
  without re-doing or skipping work.
- **Stoppable.** A clear stop signal halts the loop cleanly between iterations.

## 4. Stop conditions

A loop halts (not just sleeps) when any of these hold:

- A safety guard trips (e.g., anomalous data volume, repeated provider errors,
  a config that would touch a forbidden capability).
- Verification debt exceeds a configured threshold
  (see [verification_debt_policy.md](verification_debt_policy.md)).
- A provider signals terms/limit problems.
- A human issues a stop.

Default posture on doubt: **halt and surface**, don't push through.

## 5. Cadence and triggers

- Cadence is explicit and conservative (e.g., scheduled intervals), tuned to the
  provider's limits and the data's natural freshness, never "as fast as possible."
- Triggers are allowed (e.g., on-demand run) but obey the same guards and bounds.

## 6. Maker / checker inside the loop

`ANALYZE` is the maker; `VERIFY` is the checker, and they are separated per
[maker_checker_policy.md](maker_checker_policy.md). A candidate that fails the
checker is labeled down and/or recorded as debt — it does not flow to `REPORT`
as a verified finding.

## 7. What loops must never do

- A **research / monitoring loop** takes no financial action — ever. The gated
  **execution loop** may place orders, but **only** within pre-set hard limits +
  kill-switches, fully journaled and reconciled, instantly haltable, and
  human-operated — never unbounded, never unattended, never beyond the authorized
  limits, and never launched or operated by the assistant.
- Send outward-facing messages or publish externally without explicit approval.
- Escalate their own permissions, cadence, or scope without a human.
- Swallow errors silently; failures are recorded and, past threshold, halt.

## 8. Bootstrap status

No loops are implemented. This document is the contract any future loop must
satisfy before it is built, and a prerequisite for the relevant gate in
[promotion_policy.md](promotion_policy.md).
