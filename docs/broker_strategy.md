# Broker Strategy

Posture toward brokerage connections. For **Project_money** the concrete broker is
**Robinhood** (any other broker would be governed identically). The short version:
a broker is a **read-only data provider**, it is **gated**, and **no integration
exists today**.

## 1. Default state

**No broker integration exists. None is permitted during the documentation-only
bootstrap.** This document defines the boundary a future integration must respect
before it could ever be built — it is not an authorization to build one.

Project_money's original brief lists a "Robinhood API" among its resources. That
is scoped here to **read-only data only** — the existence of the API, or of
execution endpoints within its SDK, is **not** authorization to use them. See
[safety_policy.md](safety_policy.md).

## 2. The boundary: read-only, never an execution path

If and when a Robinhood (or other broker) connection is built, it is constrained to
**read-only market and account data** for research:

- **Allowed (future, gated):** read market data, read account *state* for
  context (e.g., to label what is already held, for research framing only), read
  historical data.
- **Never:** place, modify, or cancel orders; transfer or withdraw funds; change
  allocations; or connect any read path to an action path. The system does not
  buy, sell, trade, or execute — see [safety_policy.md](safety_policy.md). These
  capabilities are not "disabled by config"; they are simply not built.

A broker therefore appears in [architecture.md](architecture.md) as just another
**read-only provider** behind the provider interface
(see [provider_strategy.md](provider_strategy.md)), with extra caution.

## 3. Why brokers get extra caution

A brokerage API is the one provider whose vendor SDK *also* exposes execution
endpoints. That proximity is the risk. Mitigations a future integration must
include:

- Use read-only credentials / permissions where the broker supports them.
- Prefer paper/read endpoints; never instantiate execution clients.
- Keep any broker adapter in an isolated module with no import path to anything
  that could act.
- Treat account data as sensitive: no secrets, account numbers, or balances in
  the repo, logs, or reports (redact per [report_policy.md](report_policy.md)).

## 4. Gates before any broker work

Building a broker integration requires, in sequence:

1. The user explicitly lifting the bootstrap scope guard for broker work.
2. A written blueprint in [../project_blueprints/](../project_blueprints/) for
   the broker integration, reviewed against this document and the safety policy.
3. Passing the relevant gate in [promotion_policy.md](promotion_policy.md),
   including an explicit "read-only, no execution path" verification.
4. Maker/checker review confirming no execution capability is reachable.

Until all four hold, the answer to "connect a broker" is **no**.

## 5. Phasing (illustrative, not approved)

```text
Phase 0  (now)  no broker integration
Phase 1  read-only market data only        ← requires gates in §4
Phase 2  read-only account context         ← separate authorization
Phase 3+ (execution)                        ← OUT OF SCOPE for this playbook
```

Phase 3+ is explicitly outside this project's scope. Project_money is a research
system only.

## 6. Cross-references

[safety_policy.md](safety_policy.md) · [provider_strategy.md](provider_strategy.md)
· [architecture.md](architecture.md) · [promotion_policy.md](promotion_policy.md)
· [report_policy.md](report_policy.md)
