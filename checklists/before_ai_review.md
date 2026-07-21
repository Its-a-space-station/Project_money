# Checklist — Before an AI Review / Critic Pass

> **Copy / adapt into the project repo.** Documentation only. Fail-safe default:
> if any box cannot be honestly checked, stop and ask. See
> ../docs/maker_checker_policy.md.

Run this before adding an AI review / critic pass. The AI is a **checker** —
advisory only, never authoritative.

## Deterministic foundation

- [ ] **Deterministic filtering is stable** and produces reproducible results.
- [ ] **Persisted candidates and rejections exist** — the AI reviews stored state,
      not live, unrecorded data.

## Hard boundaries

- [ ] The AI **cannot override deterministic rejections**.
- [ ] The AI **cannot change config / thresholds**.
- [ ] The deterministic result remains authoritative; the AI only annotates,
      questions, or routes items to `needs_human_review`.

## Output discipline

- [ ] The AI must produce **strict JSON output** conforming to the relevant schema.
- [ ] On **invalid JSON: retry once, then log a failure** — never silently guess or
      coerce.
- [ ] **Save AI output with provenance** (model id, prompt version, timestamp,
      input ids).

## Human boundary

- [ ] The **human review boundary** is explicit: AI output informs a human and
      never triggers an action or a financial decision.
