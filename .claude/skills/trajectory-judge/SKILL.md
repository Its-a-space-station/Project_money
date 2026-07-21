---
name: trajectory-judge
description: Score a completed research trajectory 0–10 for environment-detachment (analysis paralysis, rogue batched actions, premature disengagement) and gate best-of-N selection. Use after long research runs, or when choosing among k candidate trajectories before expensive validation.
---

# Trajectory Judge — environment-detachment scoring

Implements the Overthinking paper's judge design for research trajectories.
Detachment (substituting internal simulation for environment feedback)
correlates strongly with failure (β=−7.9, R²=0.89); this skill scores it and
supports lowest-score@k selection (+30% at −43% cost in the source study).

## Protocol (follow exactly)

1. **Input**: the full trajectory (actions + observations) with the final
   outcome/verdict **removed** — never let the judge see whether the run
   "succeeded" (anti-bias, from the source design).
2. **Judge with a fresh subagent** (temperature-0 mindset: cite specific
   turns as evidence; no credit for style). The judging prompt must NOT use
   the word "overthinking" (anti-priming); it defines only the three
   manifestations below.
3. **Score 0–10** on environment-detachment:
   - **Analysis paralysis** — elaborate planning/derivation that never
     converts to executed checks (backtests designed but not run; statistics
     asserted but never computed).
   - **Rogue batched actions** — after an error, chains of interdependent
     steps emitted without awaiting output (data-pull + backtest + stats in
     one shot post-failure).
   - **Premature disengagement** — a conclusion ("edge exists" / "hypothesis
     dead") stated from reasoning alone, without the executed artifact that
     would show it.
   Bands: 0–3 = consistently interacts and waits (even stuck-loop retries
   score low here — flag those separately); 4–7 = heavy internal reasoning
   but still verifies; 8–10 = conclusions detached from execution.
4. **Output contract** (JSON): `{"score": <0-10>, "evidence": [{"turn": n,
   "category": "...", "quote": "..."}], "stuck_loop_flag": bool}`.
   A low score is necessary, not sufficient — stuck loops score low and are
   still bad; hence the separate flag.
5. **Best-of-N**: when k candidate trajectories exist, prefer the lowest
   score; log all scores to the ledger entry.

## Judge identity & bias controls (batch-3 hardening)

- **Pin the judge identity**: every score record logs model ID + prompt hash
  + sampling params. Changing ANY of the three creates a *different judge*
  and voids the calibration — re-calibrate before it gates again. A score
  shift without a pipeline change is a `needs_human_review` event, not a
  finding.
- **Bias battery** (run at each calibration cycle): (a) order-swap — for any
  pairwise/best-of-N use, score under both orderings; (b) length-confound —
  check that longer trajectories don't win on verbosity (documented judge
  bias: verbose-but-wrong beats concise-and-right); (c) anchor-set repeats —
  re-score a fixed anchor set and track run-to-run variance as a judge-health
  metric (consistency ≠ accuracy).
- **Maker ≠ judge**: the model family that produced a trajectory is never its
  sole judge (self-bias is measured at +10–25% self-win-rate).
- Prefer discrete per-criterion sub-scores (1–5 with a worked exemplar per
  level) aggregated to the 0–10 total, over one raw 0–10 judgment.

## Calibration gate (before this judge gates anything)

Score ~20 trajectories that a human has independently rated; report agreement
(rank correlation ≥ 0.8 to match the source's bar). **Authority statement
(sample-size honesty):** ~20 labels can only certify *coarse* agreement
(≈10 labels detect ~30% score gaps; ≈100 detect ~10%). At n≈20 this judge is
valid for screening and best-of-N triage ONLY — never as sole promotion
evidence. Grow the calibration set toward ~100 labels (bootstrap it to check
κ stability) before any gate-level reliance. Until calibrated, judgments are
advisory only — an uncalibrated LLM judge is never a gate.
