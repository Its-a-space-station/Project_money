# Checklist — Before a Config Change

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask.

Run this before changing any threshold, criterion, weight, or other config value.

## Identify & justify

- [ ] Identify the exact config field being changed (file + key).
- [ ] Justify the change: why now, and what evidence supports it.
- [ ] Show the **previous value and the proposed value** side by side.

## Validate

- [ ] Set / refresh the validation status: the change is `validation_pending`
      until an independent check confirms it does what is claimed.
- [ ] Verify downstream behavior — list what consumes this field and confirm the
      effect is understood (re-run on cached data where possible).

## Approve & record

- [ ] **Require human approval** before applying the change.
- [ ] Update `STATE.md` / `tasks/todo.md` / `tasks/lessons.md` if the change is
      durable.

## Guardrail

- [ ] **No silent threshold promotion.** Do not quietly widen, loosen, or relax a
      threshold; every change is explicit, justified, and reviewed.
- [ ] No config change initiates any financial action — config is research-only.
