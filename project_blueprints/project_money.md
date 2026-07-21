# Blueprint — Project_money

> **Blueprint, not implementation.** This explains how Project_money applies the
> shared Decision Systems Playbook. No code, scripts, adapters, broker
> integrations, or credentials here. The repo receives copied / adapted local
> files and remains independently auditable.

- **Project slug:** `project_money` · **object types:** `equity`, `etf`, `option`,
  `macro_signal`, `factor`

## 1. Purpose

A **research-only** quantitative strategy-discovery system. It identifies edges
from first principles, tests them with statistical rigor, and surfaces **verified,
labeled findings** for human research — never for action. It is broader than a
single screener: it spans equities, ETFs, options, macro signals, and factor
research (see `CLAUDE.md` Part II for the research doctrine).

## 2. Current phase / posture

Research-only and **offline-first**: the first slices operate on cached data and
need no live feed to function. **No provider adapters. No broker integration.**
Pre-MVP — the repo currently holds only playbook scaffolding and this blueprint.

## 3. What was copied from the playbook

- **Docs (core governance):** `architecture`, `safety_policy`, `verification_policy`,
  `label_policy`, `maker_checker_policy`, `report_policy`, `loop_architecture`,
  `claude_code_workflow`, `provider_strategy`, `broker_strategy`, `promotion_policy`,
  `verification_debt_policy`.
- **Schemas:** the full six-object set, with `project = project_money` and
  `object_type` extended for multi-asset scope.
- **Templates:** `STATE`, `tasks.todo`, `tasks.lessons`, `daily_report`,
  `weekly_report`, `manual_review`, `postmortem`, `verification_debt`.
- **Checklists:** bootstrap, safe checkpoint, and the before-{config change,
  provider adapter, scheduling, AI review, paper workflow, broker integration} set.
- **Not copied (deferred):** the v2 / v2.1 / v2.2 layers (engineering discipline,
  forecasting, macro / market-structure). They remain in the shared playbook.

## 4. Project-specific safety rules

- Research-only; offline-first; **no autonomous financial action**.
- **Robinhood is read-only, gated, and treated as a broker** — no execution path,
  isolated from any code that could act (see `broker_strategy`).
- Tiingo and FRED are **read-only** providers; respect terms and rate limits.
- **No buy / sell / trade / order labels** — use the canonical labels only.
- No secrets or account data in the repo, logs, or reports.

## 5. Approved canonical labels

Use only: `reject`, `watchlist`, `trigger_ready_research_candidate`,
`needs_human_review`, `paper_candidate`, `research_only`, `validation_pending`.

Typical mapping:

| Label | Project_money meaning |
| --- | --- |
| `trigger_ready_research_candidate` | Meets the full deterministic criteria set; surfaced for research. |
| `watchlist` | Developing setup / partial criteria; monitor. |
| `needs_human_review` | Borderline or conflicting signals. |
| `reject` | Fails criteria or data-quality screen. |
| `validation_pending` | Data gap or incomplete verification; cannot confirm. |
| `research_only` / `paper_candidate` | Retained for study or paper tracking. |

## 6. Near-term build sequence (each step gated on authorization)

1. Project docs (done — adopted from the playbook).
2. Cached-data validator (integrity, adjustments, **no lookahead**).
3. Config / data contract (the schema a research slice depends on).
4. Feature engine (deterministic, reproducible indicators / signals).
5. Research-only screen/analysis (applies criteria → canonical labels).
6. Markdown reports (research-only warning + safety footer).
7. Manual review of `needs_human_review` / borderline items.
8. Calibration (criteria performance, false positives / negatives, postmortems).

## 7. Later build sequence

1. **Tiingo / FRED adapters** — read-only providers behind the provider interface;
   respect terms and rate limits (see `provider_strategy`).
2. **Robinhood read-only importer** — market data and the human's *own* past
   account context, imported read-only for research comparison, with **no
   execution path** (see `broker_strategy`).
3. Possibly adopt the playbook's **v2.1 forecasting** layer if ML / time-series
   forecasting is authorized (advisory only; creates no execution authority).

## 8. Explicit non-goals

- No order placement, fund movement, or position changes — ever.
- No broker execution client; Robinhood stays read-only and gated.
- No live-data dependency to function (offline-first by design).
- No action-word labels.

## 9. Verification expectations

- The cached-data validator is the first line of verification: it guards against
  **lookahead** and bad adjustments before any feature is computed.
- Feature engine and screens are deterministic and reproducible; maker / checker
  are separated (no AI override of deterministic logic).
- **Survivorship bias** (delisted tickers), **lookahead**, and **overfitting /
  multiple-testing** risk are tracked explicitly in the verification-debt ledger.
- Out-of-sample and walk-forward validation are required before any edge is
  treated as real (see `CLAUDE.md` §15 Evidence standards).

## 10. What "real-life value" means here

A disciplined, reproducible, bias-controlled stream of research candidates and
strategy evaluations — free of lookahead and survivorship distortion — that a
human studies and decides on. Value is trustworthy evidence for human research,
never instructions to act.
