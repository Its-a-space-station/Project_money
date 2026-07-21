# Skill & Lessons Evolution Policy

> How this project's skills, lessons, and research procedures are allowed to
> improve over time — the gated version of what Live-SWE/EvoSkill/DGM/Bilevel
> demonstrate (see [agent_tooling_synthesis.md](agent_tooling_synthesis.md)
> §3.5, §4 tool 11, §6.3). Evolution adds reliability, never autonomy.
> Research-only; the human stays curator.

## 1. What may evolve

Skills (`.claude/skills/`), subagent definitions (`.claude/agents/`), lessons
(`tasks/lessons.md`), prompts, and evaluation configs. **What may never
evolve on its own**: the safety policies, the label set, the finding hook,
scope guards, or anything in Part I of CLAUDE.md — those change only by
explicit human edit.

## 2. The reflection lever (cheap, high-yield)

During research work, after each substantial feedback observation, ask: "would
a small script/skill/checklist item make the rest of this task faster or
safer?" (Live-SWE's per-step reflection carried +14pp — the *capability*
without the reflection was worth only +2pp.) Ephemeral per-task helpers need
no ceremony; they die with the task.

## 3. The promotion boundary (where the gate lives)

An ephemeral helper, new skill, or lesson becomes **persistent** only through
this gate (the gate Live-SWE lacks):

1. **Provenance**: it emerged from a task whose finding/outcome passed
   verification (a helper from a failed investigation may still be proposed,
   flagged as such).
2. **Held-out check**: demonstrated benefit on a case it was not derived from
   (EvoSkill's admission rule: improve held-out validation or the branch is
   deleted). For lessons: the tasks/lessons.md rule — a lesson earns
   permanence when it helps on a later case; prune those that never fire.
3. **Proposal ledger**: the change is registered (reuse
   `project_money.ledger.HypothesisLedger` with `family="skill_evolution"`),
   citing any DISCARDED sibling it differentiates from — anti-churn
   (EvoSkill's feedback history; Bilevel's 22-identical-discards pathology).
4. **Validate-and-revert with verified activation**: apply the change, run the
   relevant smoke checks (for skills: does the workflow still pass its
   bracket cases?), and **assert the change actually took effect** — silent
   fallback invalidated an entire experiment in the source literature. Revert
   is one `git checkout` (every config change is a commit).
5. **Human sign-off**: the user approves what persists. Naive self-curation
   regresses (SWE-Gym 15.3→8.7%).

## 4. Bounds (hard, not advisory)

Any evolution loop is bounded: max iterations per session, max helpers per
task (K-without-progress breaker), no background/scheduled evolution, and
never enabled for weak-model sessions (the mechanism collapses below
frontier-class backends: 44→14% in the source).

## 5. Diversity over convergence

Keep independently derived variants; merge from independent runs rather than
keeping only the latest winner (cross-run merge was EvoSkill's best result;
DGM's archive beat greedy by ~10 points). `tasks/lessons.md` keeps competing
approaches alive until evidence retires one.
