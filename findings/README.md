# findings/

Machine-checkable research finding records (JSON objects, one file per
finding). Two PreToolUse hooks (`hooks/validate_finding.py` and
`hooks/guard_findings_bash.py`, wired in `.claude/settings.json`) enforce at
write time:

- `label` must be canonical (see [../docs/label_policy.md](../docs/label_policy.md));
- labels other than `validation_pending`, `needs_human_review`, `reject` are
  **promotions** and require ALL of: a non-empty `maker`, a non-empty
  `verification.checker` distinct from `maker`, and a
  `verification.artifact_path` that lives under `outputs/`, exists, and parses
  as JSON (the executed cascade/falsification output);
- findings are rewritten whole (`Write`); Edit-family tools are blocked, and
  shell writes into `findings/` are blocked heuristically;
- only this exact file (`findings/README.md`) is exempt;
- once a write targets `findings/`, hook errors **fail closed** (block).

Defense in depth, not proof: the Bash guard is heuristic and hooks can be
disabled in settings — the final gates remain human review and `git diff`
before any commit of findings/.

## Record shape (minimum)

```json
{
  "id": "a1b2c3d4e5f6",
  "ts": "2026-07-20T00:00:00Z",
  "family": "momentum",
  "hypothesis": "one-sentence statement of the claimed edge",
  "label": "validation_pending",
  "maker": "strategy-analyst",
  "scores": {"stage0.score": 1.0},
  "verification": {
    "artifact_path": "outputs/cascade/a1b2c3d4e5f6.json",
    "checker": "research-validator"
  },
  "provenance": {"data": ["prices_v1"], "ledger_entry": "h17"}
}
```

`id` should be `project_money.memory.stable_id(...)` of the hypothesis +
params. Full evidence/belief structure lives in [../schemas/](../schemas/);
this record is the promotion-gated summary that reports cite by pointer.

Research-only: a finding describes what was observed and how confident we are.
It never directs an action.
