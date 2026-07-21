# Promotion Policy

How work moves from idea to standard. Promotion is the gated path that prevents
half-verified experiments from becoming load-bearing. Nothing advances a stage
without passing that stage's gate.

## 1. Stages

```text
  EXPERIMENT  ──▶  CANDIDATE  ──▶  STANDARD  ──▶  OPERATIONAL
  (sketch)         (reviewed)      (blueprint)    (running loop)
```

| Stage | Meaning |
| --- | --- |
| **Experiment** | An exploratory doc, schema, or (later) prototype. No reliance. |
| **Candidate** | Reviewed against the policies; internally consistent. |
| **Standard** | Adopted into the playbook / a project blueprint as the way we do it. |
| **Operational** | A live research loop producing findings (future). |

## 2. Gates

Each promotion requires meeting **all** criteria for the target stage.

### → Candidate

- Conforms to [architecture.md](architecture.md) and uses approved vocabulary
  ([label_policy.md](label_policy.md)).
- Cross-links resolve; no contradictions with existing policies.
- Reviewed by an independent pass (maker ≠ checker,
  [maker_checker_policy.md](maker_checker_policy.md)).

### → Standard

- Everything in Candidate, plus:
- Documented in the right home (a `docs/` policy, a `schemas/` shape, or a
  `project_blueprints/` plan).
- [STATE.md](../STATE.md) and [tasks/todo.md](../tasks/todo.md) updated.
- No open `Conflicting` items against it.

### → Operational (future; requires lifting bootstrap scope guard)

- Everything in Standard, plus:
- Satisfies [loop_architecture.md](loop_architecture.md) (bounded, idempotent,
  observable, stoppable).
- Satisfies [verification_policy.md](verification_policy.md) with maker/checker
  separation in place.
- Provider use complies with [provider_strategy.md](provider_strategy.md);
  any broker use complies with [broker_strategy.md](broker_strategy.md).
- Verification debt is within threshold
  ([verification_debt_policy.md](verification_debt_policy.md)).
- **Reaffirms [safety_policy.md](safety_policy.md): no execution path exists.**
- Explicit user authorization to run.

## 3. Demotion

Promotion is reversible. Demote when a gate is later violated — e.g., a policy
contradiction surfaces, verification debt blows past threshold, a provider's
terms change, or a safety concern is raised. Demotion is not failure; it keeps
the standard honest. Record demotions in [tasks/lessons.md](../tasks/lessons.md).

## 4. Who decides

- Experiment → Candidate → Standard: Claude Code may propose; an independent
  review pass plus the user's acknowledgement settles it.
- Anything → Operational, and anything touching providers, brokers, money, or
  outward-facing actions: **the user must explicitly authorize.**

## 5. Bootstrap status

The entire playbook is currently at **Standard (documentation)** at most; nothing
is Operational. The bootstrap scope guard in [../CLAUDE.md](../CLAUDE.md) blocks
the Operational stage until the user lifts it.

## 6. Cross-references

[safety_policy.md](safety_policy.md) · [verification_policy.md](verification_policy.md)
· [verification_debt_policy.md](verification_debt_policy.md) ·
[maker_checker_policy.md](maker_checker_policy.md) ·
[loop_architecture.md](loop_architecture.md)
