# Claude Code Workflow

How a Claude Code session should operate inside this playbook and the projects
it governs. The goal is small, verifiable steps with a clear paper trail.

## 1. The core loop

```text
PLAN → SMALL CHANGE → VERIFY → RECORD → (repeat) → REPORT & STOP
```

1. **Plan.** Restate the goal. Identify the smallest next change. Note which
   policies apply (safety, verification, labels). If the request touches a
   safety boundary, stop and ask before proceeding.
2. **Small change.** Make one coherent change. Prefer documentation and schemas
   over speculative code. Do not exceed the authorized scope.
3. **Verify.** Confirm the change does what it should against the relevant policy
   (see [verification_policy.md](verification_policy.md)). For docs, that means
   internal consistency and correct cross-links; for code (later), that means
   tests and observed behavior.
4. **Record.** Update [../tasks/todo.md](../tasks/todo.md), append durable
   insights to [../tasks/lessons.md](../tasks/lessons.md), and keep
   [../STATE.md](../STATE.md) current.
5. **Report & stop.** Show `git status --short` and `git diff --stat`. Do **not**
   stage or commit unless explicitly asked.

## 2. Standing rules

- **Documentation-only bootstrap.** No implementation code, provider adapters,
  or broker integrations until the user lifts the scope guard in
  [../CLAUDE.md](../CLAUDE.md).
- **Maker ≠ checker.** Anything that produces a conclusion gets an independent
  verification pass before it is surfaced. See
  [maker_checker_policy.md](maker_checker_policy.md).
- **Approved vocabulary only.** No Buy/Sell/Trade/Order outside safety negations.
  See [label_policy.md](label_policy.md).
- **No secrets.** Never read, write, echo, or commit credentials. If a task
  seems to need one, stop and ask how it should be supplied at runtime.

## 3. Git discipline

- The first commit is **documentation-only**.
- Keep commits small and scoped to one logical change.
- Before finishing any unit of work, run and report:
  - `git status --short`
  - `git diff --stat`
  - `git diff --check` (whitespace / conflict-marker sanity)
- Ask the user before staging (`git add`) or committing. Never push unless asked.
- Suggested commit message style: `docs: <area> — <concise change>`.

## 4. Definition of done (per change)

- The change is within authorized scope.
- Relevant policies were applied and cross-links resolve.
- Working notes and STATE updated.
- Git status reported; nothing staged/committed without approval.

## 5. When to escalate to the user

- Any request that could cause an irreversible or outward-facing action.
- Any request to begin a build phase (providers, broker data, execution) not yet
  authorized in `STATE.md`.
- Any ambiguity about a safety boundary — default to the conservative reading and
  the division of labor in [safety_policy.md](safety_policy.md) §1 (the assistant
  builds and validates; the human operates live capital), and confirm.
