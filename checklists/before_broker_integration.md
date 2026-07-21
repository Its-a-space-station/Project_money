# Checklist — Before Broker Integration

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask. The governing policy is
> ../docs/broker_strategy.md. The default answer to "connect a broker" is **no**.

Run this before considering any broker (here, Robinhood) work.

## Gate: authorization

- [ ] Broker work is **documentation-only until explicitly approved** by the user
      in a separate authorization step.

## Maturity prerequisites

- [ ] The **research system is mature** — stable reports, manual review, calibration.
- [ ] A **trade journal exists** — a read-only record of the human's **own past
      activity**, for research comparison only.
- [ ] A **paper workflow exists** and has been run.
- [ ] **Validation evidence exists** — tracked outcomes and postmortems.

## Read-only boundary

- [ ] **Read-only import comes before any paper integration**; the read path has no
      route to anything that could act.
- [ ] **No credentials in the repo** (or logs / reports).
- [ ] **No autonomous live order placement** — the system never places, modifies,
      cancels, or submits an order, and never moves funds.

## Far-future, gated

- [ ] **Human-confirmed action only, much later, if explicitly approved** — at most
      a draft a human independently reviews and submits themselves. Never
      autonomous, and out of scope for this playbook.
