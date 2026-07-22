# Provider Strategy

How decision systems obtain external data. Providers sit at the bottom of the
architecture (see [architecture.md](architecture.md)) and are deliberately kept
**abstract and swappable**. No provider adapters exist yet, and none are to be
added during the documentation-only bootstrap.

## 1. Principle: code to an interface, not a vendor

Every system codes against a **provider interface**, never directly against a
concrete vendor SDK or endpoint. This keeps vendors swappable, keeps rate-limit
and caching logic in one place, and keeps the rest of the pipeline ignorant of
where data came from.

A provider, conceptually, exposes:

```text
provider.fetch(request) -> RawObservation        # raw, untyped-ish payload
provider.capabilities() -> { rate_limits, freshness, fields, terms_url }
provider.health()       -> { ok, latency, last_error }
```

Normalization (not the provider) maps `RawObservation` to canonical schemas in
[../schemas/](../schemas/).

## 2. Hard rules

- **Read-only.** Providers supply data. They are never an action sink. A broker
  is treated as a read-only provider (see [broker_strategy.md](broker_strategy.md)).
- **Respect terms & limits.** Honor each provider's terms of service and rate
  limits. No detection-evasion, no circumventing access controls, no prohibited
  scraping. See [safety_policy.md](safety_policy.md).
- **No secrets in the repo.** Credentials come from environment / local config
  that is git-ignored. Never commit or log a key.
- **Graceful degradation.** On error or limit, back off, label affected data
  `Stale`/`Unverified`, and record debt — never fabricate or guess.

## 3. Cross-cutting concerns (handled at the provider layer)

- **Rate limiting & backoff** — centralized, conservative, per-provider.
- **Caching** — cache responses within their freshness window to minimize calls;
  cache keys include the request and a fetched-at timestamp.
- **Retries** — bounded, idempotent, with jitter; never a tight retry storm.
- **Provenance** — stamp every datum with source id and fetch timestamp so
  verification (see [verification_policy.md](verification_policy.md)) can trace it.
- **Health & metrics** — surface provider health to the loop and reports.

## 4. Provider landscape (for orientation only — nothing to build yet)

| Provider | Data domain | Notes |
| --- | --- | --- |
| Tiingo | Equity / ETF prices, fundamentals, news | Read-only; respect terms & rate limits; licensed market data. |
| FRED | Macro / economic time series | Read-only; public data; cite series ids. |
| Robinhood | Market data + own-account context; **execution is the gated destination** | Read-only data first; the human-operated order path is built later per the gated ladder in [broker_strategy.md](broker_strategy.md) §3 (assistant builds/validates, never operates live or holds credentials). |

This table is **orientation, not authorization**. Adding any adapter requires
lifting the bootstrap scope guard and passing the relevant promotion gate.
**Robinhood is the single highest-caution provider here** — its vendor SDK also
exposes execution endpoints, so it is governed by [broker_strategy.md](broker_strategy.md),
not just this document.

## 5. Selection criteria (when the time comes)

Prefer providers with: clear and permissive terms for our research use,
documented rate limits, stable schemas, good data freshness/coverage, and
sane authentication. Avoid providers whose terms prohibit our use or that require
evasion to access.

## 6. Cross-references

[architecture.md](architecture.md) · [safety_policy.md](safety_policy.md) ·
[broker_strategy.md](broker_strategy.md) ·
[verification_policy.md](verification_policy.md) ·
[loop_architecture.md](loop_architecture.md) ·
[promotion_policy.md](promotion_policy.md)
