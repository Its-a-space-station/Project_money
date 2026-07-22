# Broker Strategy

Posture toward the brokerage connection. For **Project_money** the broker is
**Robinhood** (any other broker would be governed identically). The short version:
the broker provides **read-only data first**, and **execution is the destination**
— built later, gated phase by phase, and **operated by the human**. The assistant
builds and validates the execution path but never operates it live or holds
credentials (see [safety_policy.md](safety_policy.md) §1).

## 1. Two roles, sequenced

The broker serves two roles, built in order:

1. **Read-only data provider (first).** Market data, and account *state* for
   context (what is held, buying power) — behind the read-only provider interface,
   with extra caution because the same SDK exposes execution.
2. **Execution venue (the destination).** Order placement for validated
   strategies, built through the gated ladder in §3 and operated by the human.

Role 1 is built and used first; Role 2 is unlocked only phase by phase.

## 2. Extra caution for the broker

A brokerage API is the one provider whose vendor SDK *also* exposes execution
endpoints. That proximity is the risk. Mitigations, at every phase:

- Keep read paths and order paths in **separate modules**; the read/research layer
  has no import path that can place an order.
- Use the narrowest credentials/permissions the broker supports for the current
  phase (read-only until execution is authorized).
- Treat account data as sensitive: no secrets, account numbers, or balances in the
  repo, logs, or reports (redact per [report_policy.md](report_policy.md)).
- Credentials are supplied by the human at runtime and never handled by the
  assistant (safety_policy.md §1, §5).

## 3. The gated ladder to execution

Each rung requires explicit human authorization recorded in `STATE.md`; nothing
advances by inference.

```text
Phase 0  read-only market data
Phase 1  read-only account context (buying power, positions, for research)
Phase 2  dry-run execution         (orders computed + journaled, never sent)
Phase 3  paper trading             (broker paper endpoint or simulator; no real money)
Phase 4  shadow-canary             (live-data signals logged, still no real orders)
Phase 5  human-approved live       (real orders, each trade/batch approved by the human)
Phase 6  bounded auto-trade        (looped, within hard limits + kill-switches) — a
                                    later, separately authorized graduation
```

**Live equities begin at Phase 5 (human approves each trade/batch).** Phase 6 is
earned only after a live track record under Phase 5 and an explicit decision — it
is never the starting point.

## 4. Guardrails any execution build must include

Before real money (Phase 5+), the execution module must have — and the assistant
must build — the full guardrail set (the user's Kalshi trading bot is the working
reference for this pattern):

- **Kill-switches:** global and per-category daily-loss limits, drawdown limit,
  consecutive-loss limit; a manual halt that persists across restarts.
- **Position / exposure limits:** per-ticker cap, total-exposure cap, fractional
  Kelly or equivalent sizing bound, price bounds.
- **Shadow-canary promotion:** a mandatory shadow period with pre-registered
  promotion criteria (minimum days, minimum resolved sample, out-of-sample
  improvement over honest nulls, zero safety events) before anything goes live;
  features default off.
- **Journaling & reconciliation:** every order event recorded; local equity /
  positions reconciled against the broker; mismatch triggers a halt.
- **Dry-run mode** and a documented **runbook** with emergency-stop and flatten
  procedures.

An execution build lacking any of these does not reach Phase 5.

## 5. Validation is the precondition

No strategy is wired to Phase 5+ until it has cleared the full verification stack
(safety_policy.md §2): maker ≠ checker, deflated Sharpe, leakage/contamination
audit, cost-inclusive evaluation, and contamination-free forward tracking. The
broker path executes *validated* strategies; it does not validate them.

## 6. Cross-references

[safety_policy.md](safety_policy.md) · [provider_strategy.md](provider_strategy.md)
· [architecture.md](architecture.md) · [promotion_policy.md](promotion_policy.md)
· [report_policy.md](report_policy.md) · [loop_architecture.md](loop_architecture.md)
