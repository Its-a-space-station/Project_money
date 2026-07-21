# Lessons — Project_money

> Append durable insights a future session would be worse off not knowing. Prefer
> adding a dated note over rewriting history. Not executable automation.

## Format

```text
### YYYY-MM-DD — Short title
**Context:** what we were doing.
**Lesson:** what we learned.
**Apply:** how to act on it next time.
```

## Workflow lessons

### 2026-07-20 — Adopted the Decision Systems Playbook (tailored bootstrap)

**Context:** Project_money began as a single quant-research brief (`.rtf`). We
adopted the shared playbook's structure, architecture, and philosophy.
**Lesson:** The playbook is a *governance layer* meant to be inherited; the
project's own quant doctrine is the *domain layer*. They compose cleanly when
kept as distinct parts of `CLAUDE.md` with safety rules taking precedence.
**Apply:** When pulling in more playbook layers later (v2 forecasting, macro),
keep governance vs. domain separation and re-run the cross-link check.

### 2026-07-20 — Localize + link-trim when inheriting shared docs

**Context:** Adopting the playbook copied docs written for a *family* of systems;
they carried sibling-system examples (eBay/Minervini/Polymarket/Kalshi/IBKR) and
cross-links to uncopied v2 layers.
**Lesson:** Verbatim inheritance leaves two defects — dangling cross-links to files
you didn't copy, and sibling references that misread this repo as multi-system.
**Apply:** After any future playbook pull, (1) run a repo-wide relative-link scan
and trim/repoint links to uncopied targets, and (2) grep for sibling-system names
and localize them to Project_money. Both were run this session and are green.

## Safety lessons

### 2026-07-20 — Robinhood is a broker, not just a data API

**Context:** The original brief lists a "Robinhood API" as an available resource.
**Lesson:** Robinhood's SDK also exposes order/fund execution endpoints. Under the
playbook, a broker is a **read-only, gated data provider** and never an action
sink; capability existing is not authorization.
**Apply:** Any Robinhood usage is read-only data only, isolated from any code that
could act, gated behind [docs/broker_strategy.md](../docs/broker_strategy.md).
Never instantiate an execution client.

## Project-specific lessons

_None yet._

## Repeated mistakes to avoid

- Treating an available API/credential as authorization to use its write paths.
- Promoting a self-attested result past `validation_pending` without an
  independent checker.
- Using action words (buy/sell/trade/order) as labels or field names.
