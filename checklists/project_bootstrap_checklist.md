# Checklist — Project Bootstrap

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask. Keep the first commit
> documentation-only.

Run this when starting a new project repo from the shared playbook.

## Purpose & scope

- [ ] Confirm the project purpose in one sentence (research-only; informs a human,
      never acts).
- [ ] Confirm the current phase / posture (e.g., Bootstrap, research-only).

## Copy / adapt the scaffolding

- [ ] Copy / adapt the CLAUDE template → `CLAUDE.md`; replace every `{{PLACEHOLDER}}`.
- [ ] Copy / adapt the STATE template → `STATE.md`.
- [ ] Create `tasks/todo.md` and `tasks/lessons.md` from the task templates.
- [ ] Copy the governing docs: `safety_policy`, `verification_policy`,
      `label_policy`, `maker_checker_policy`, `report_policy` (plus
      `provider_strategy` / `broker_strategy` if relevant later).

## Schemas & boundaries

- [ ] Choose the relevant canonical schemas; set `project` and `object_type`.
- [ ] Define explicit **non-goals** (what this project will not do).
- [ ] Define the first **MVP** — the smallest deterministic, verifiable slice.

## Verify & commit

- [ ] Run initial verification: docs internally consistent, cross-links resolve,
      labels are canonical, no secrets.
- [ ] Commit the **documentation-only** bootstrap using **explicit staged paths**
      (no `git add -A`); ask before staging and before committing.

## Reminders

- [ ] No code modules, provider adapters, or broker integrations in the bootstrap.
- [ ] No autonomous financial action anywhere in scope.
