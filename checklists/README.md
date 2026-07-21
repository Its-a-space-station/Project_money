# checklists/

Short, practical checklists that turn the playbook's policies into do-this-now
steps. Each one is **copied / adapted into an individual project repo** and run at
the moment named in its title. Documentation only — not executable automation.

**Default rule for every checklist: if any box cannot be honestly checked, stop
and ask.** The shared safety policy wins on any conflict.

## Status

**Lean checklist set present.** Eight operational checklists were adopted (the
core v1 set). The playbook's v2 / v2.1 / v2.2 checklists (dynamic workflow,
task-spec, verifier, complexity, forecasting, macro / structural-break, etc.) were
**not** copied — they live in the shared playbook and can be adopted later.

## The checklists (when to use each)

| Checklist | Run when… |
| --- | --- |
| [project_bootstrap_checklist.md](project_bootstrap_checklist.md) | Starting a new project repo from the playbook |
| [safe_checkpoint_checklist.md](safe_checkpoint_checklist.md) | Finishing any unit of work, before staging / commit |
| [before_config_change.md](before_config_change.md) | Changing a threshold / criterion / config value |
| [before_provider_adapter.md](before_provider_adapter.md) | Adding a read-only data provider (Tiingo / FRED) |
| [before_scheduling.md](before_scheduling.md) | Adding a scheduled / automated runner |
| [before_ai_review.md](before_ai_review.md) | Adding an AI review / critic pass |
| [before_paper_workflow.md](before_paper_workflow.md) | Starting paper-only opportunity tracking |
| [before_broker_integration.md](before_broker_integration.md) | Considering any broker (Robinhood) work |

## Rules every checklist enforces

- **Explicit-path staging only.** No `git add -A` / `git add .` unless explicitly
  approved. No push without a separate approval.
- **Verification before "done."**
- **No autonomous financial action.**
- **Canonical labels only**, where labels are needed (see
  [../docs/label_policy.md](../docs/label_policy.md)): `reject`, `watchlist`,
  `trigger_ready_research_candidate`, `needs_human_review`, `paper_candidate`,
  `research_only`, `validation_pending`.

## Cross-references

Workflow: [../docs/claude_code_workflow.md](../docs/claude_code_workflow.md) ·
Safety: [../docs/safety_policy.md](../docs/safety_policy.md) ·
Verification: [../docs/verification_policy.md](../docs/verification_policy.md) ·
Providers: [../docs/provider_strategy.md](../docs/provider_strategy.md) ·
Brokers: [../docs/broker_strategy.md](../docs/broker_strategy.md) ·
Loops: [../docs/loop_architecture.md](../docs/loop_architecture.md) ·
Templates: [../templates/](../templates/) · Blueprints: [../project_blueprints/](../project_blueprints/)
