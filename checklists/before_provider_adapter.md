# Checklist — Before a Provider Adapter

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask. See
> ../docs/provider_strategy.md.

Run this before adding any read-only data provider.

## Foundation first

- [ ] The **offline pipeline works first** — the system functions end-to-end on
      cached data before a live provider is introduced.
- [ ] The provider's output is **normalized into cached data**; downstream logic
      reads the cache, not the provider.

## Credentials & safety

- [ ] Credentials are supplied **via environment only**.
- [ ] **No API keys or secrets in the repo** (or in logs, reports, fixtures).
- [ ] **No live API calls in unit tests.**
- [ ] Tests use **mocked / static fixtures**.

## Boundaries

- [ ] The provider **does not compute signals or assign labels** — it only fetches
      and shapes raw data.
- [ ] The provider **does not bypass verification / validation** — normalized data
      still goes through the maker / checker path.
- [ ] The provider is **read-only**; it is never an action sink.
- [ ] Provider terms of service and rate limits are respected; no detection-evasion.
