# Checklist — Safe Checkpoint

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask.

Run this when finishing any unit of work, before staging or committing.

## Inspect the working tree

- [ ] `git status --short`
- [ ] `git diff --stat`
- [ ] `git diff --check` (whitespace / conflict-marker sanity)

## Review

- [ ] Review each changed file deliberately.
- [ ] Identify risky files: anything touching secrets, safety wording, labels,
      thresholds, or outward-facing output.
- [ ] Confirm changes stay within the authorized scope for this phase.

## Stage & commit (explicit paths only)

- [ ] Propose the explicit list of paths to stage (name them).
- [ ] **No blind `git add -A` / `git add .`** unless explicitly approved.
- [ ] Re-verify staged content: `git diff --cached --stat`, `git diff --cached --check`.
- [ ] Commit **only after** human approval; use a concise, scoped message.

## Push

- [ ] Push **only after a separate** human approval.
- [ ] Confirm tracking after push (`git status -sb` shows in sync).
