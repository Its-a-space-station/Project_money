# Checklist — Before Scheduling

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask. See
> ../docs/loop_architecture.md.

Run this before adding any scheduled / automated runner.

## Stability prerequisites

- [ ] **Manual runs are stable** and produce consistent results.
- [ ] **State persistence is reliable** — re-running a window is idempotent.
- [ ] **Logs are clean** and useful for debugging.
- [ ] **Reports are useful** to a human reviewer.

## Bounds & failure handling

- [ ] **Timeouts are defined** per iteration.
- [ ] **No infinite retries** — retries are bounded with backoff.
- [ ] **Failure handling exists** — the loop halts and surfaces on repeated errors
      or tripped guards.

## Safety

- [ ] The scheduled run is **read-only / report-only** — it produces findings and
      reports, never an action.
- [ ] **Human approval is required** to enable scheduling.
- [ ] Note: a Mac mini with `launchd` (or any scheduler) is an example **runner** —
      it provides cadence only; it is **not a decision-maker** and grants no new
      capability.
- [ ] No scheduled run may take any financial action.
