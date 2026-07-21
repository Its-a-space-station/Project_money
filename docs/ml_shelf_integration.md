# ML Shelf Integration — batch 3 verification & extraction

> **Research documentation (information batch 3).** The 20-PDF AI/ML shelf
> (`~/Documents/Github book on AI_ML engineering/`) was already mapped by the
> playbook's `reference_library.md` (2026-07-19). This batch therefore ran a
> **verify-and-extract** pass (2026-07-21, four agents): confirm the map's
> load-bearing citations against the sources (maker ≠ checker), extract
> implementation-grade detail the built stack can absorb now, and lay the
> LLM-engineering foundation for subsequent uploads. The playbook map remains
> the canonical shelf index; this document records what the verification
> changed and what Project_money adopts. Research-only throughout.

## 1. Verdict

The prior map is **substantially verified** — every major claim's content
held. The pass caught **five citation defects** in the map, and, more
importantly, **three defects in our own stack** that are corrected in this
change set:

**Map defects (report upstream to the playbook):**
1. **minTRL is not in the de Prado book** — it lives in Bailey & López de
   Prado (2012), *The Sharpe Ratio Efficient Frontier*, J. Risk 15(2). The
   book carries PSR/DSR only.
2. **Powell subsection cites mixed conventions**: §9.9/§9.12 were cited by
   *printed* page but labeled "PDF." Correct rule: Powell PDF = printed + 20
   (so §9.9 → PDF 393, §9.12 → PDF 398–403).
3. **Optimizer's-curse depth drift**: R&N 3e mentions it only in
   bibliographical notes (no formula). The shrinkage correction must be
   sourced to Smith & Winkler (2006).
4. **Offset corrections**: Mohri = printed +17→+18 (not +15); DasGupta =
   printed +24 (not +21). Confirmed exact: de Prado +27, Powell +20, S&B +22,
   R&N +19, Murphy-Intro +30, Murphy-Adv +33.
5. Minor: Tunstall's never-resample-before-split line is p. 48 (not 49–51);
   Huyen's judge-calibration mandate spans Ch 3 *and* Ch 4.

**Stack defects (corrected in this change set — see §3):**
1. **`deflated_sharpe` benchmark mis-specified.** We used
   `sr_std = sqrt(1/n_periods)`; the book requires **√V[{SR_n}] — the
   empirical variance of Sharpe estimates across recorded trials**. Our gate
   was *anti-conservative* exactly when trials are diverse (the dangerous
   direction) and over-conservative for near-clone trials.
2. **Kurtosis-convention hazard.** The DSR formula takes *raw* kurtosis
   (Gaussian = 3); `compute_metrics` emits pandas *excess* kurtosis. Feeding
   one into the other silently corrupts the denominator.
3. **Trajectory-judge authority overstated.** With ~20 human calibration
   labels, κ ≥ 0.8 certifies only coarse agreement (~10 labels detect 30%
   score gaps; ~100 detect 10% — Huyen Table 4-7). The judge is valid for
   screening/best-of-N triage, not as sole promotion evidence, until the
   calibration set grows toward ~100.

Also confirmed: the two Sutton & Barto PDFs are byte-identical (same MD5);
one can be deleted at the user's discretion.

## 2. Corrections applied to the stack (this change set)

1. `validation/metrics.py::deflated_sharpe` — accepts `trial_sharpes` (the
   ledger's recorded per-trial Sharpes); when provided, the benchmark uses
   the empirical cross-trial variance per the book. Without it, the IID
   zero-edge null approximation `sqrt(1/n_periods)` is used and documented as
   a fallback that understates the bar for diverse trials. Raw-kurtosis
   validation added (`kurtosis >= 1` mathematically; excess input raises with
   a corrective hint).
2. `validation/metrics.py::compute_metrics` — emits `kurtosis_raw`
   (= excess + 3) alongside the existing key so the DSR input is directly
   available and the convention is explicit.
3. `ledger/hypothesis_ledger.py::recorded_sharpes` — extracts per-trial
   Sharpe estimates from the ledger, wiring the trial registry to the
   corrected DSR exactly as de Prado's "Third Law" requires.
4. `.claude/skills/trajectory-judge/SKILL.md` — judge identity pinning
   (model + prompt hash + params logged per score; any change forces
   re-calibration), bias battery (order-swap, length-confound, anchor-set
   repeat variance), authority statement (screening/triage until ~100
   calibration labels), discrete per-criterion sub-scores.

All corrections carry regression tests; suite green and deterministic.

## 3. Consolidated build list (merged from the four agents' rankings)

**Applied now (this change set):** corrected DSR + kurtosis guard + ledger
wiring; judge hardening (above).

**Next (cheap, high value — build when validation work resumes):**
1. **PSR alongside DSR**, both gating at 0.95 (formulas verified; algebra on
   what exists). minTRL from the 2012 paper as a report field.
2. **F_t-measurability predicate** as the leakage-audit invariant: every
   signal at t must be a function of state known at t (Powell §9.12) — a
   one-line doctrine addition to the cascade spec; our lookahead detector is
   its executable test.
3. **Selection/valuation fold split** in candidate ranking ("never select and
   evaluate with the same estimate," S&B §6.7) + **optimizer's-curse
   shrinkage** (posterior-mean ranking; Smith & Winkler 2006) — de-biases the
   ranking stage; maker ≠ checker made numeric.
4. **Permutation p-values with the (b+1)/(n+1) correction** and mandatory
   block permutation under serial dependence (DasGupta §19.1.2; our
   falsification harness already blocks — add the corrected estimator).
5. **ROPE effect-size gate** (`p(|Δ| > ε | D)` with ε = minimum net-of-cost
   edge; closed-form Student-t posterior on paired per-fold results) —
   "economically meaningful, not just significant" (Murphy-Intro §5.2.6).
6. **Calibration harness** (reliability diagram + ECE + temperature/isotonic)
   for judge scores and belief-card confidence — makes "confidence" a
   measured quantity (Murphy-Adv §14.2.2).

**Later (moderate/expensive, high value):**
7. **PBO via CSCV** (needs per-trial aligned PnL matrices in the ledger; the
   algorithm itself is small — S=16 → 12,870 splits).
8. **CPCV backtest engine** (N groups choose k, φ = (k/N)·C(N,N−k) paths →
   Sharpe *distribution* per candidate; start N=φ+1, k=2).
9. **Triple-barrier labels + uniqueness/concurrency weights** (one shared t1
   interval object powers labeling, the exact 3-condition purge rule, and
   honest effective-sample-size discounting — overlapping events must not
   count as independent evidence).
10. **Empirical-Rademacher sign-flip capacity estimate** as a third capacity
    measure beside MDL bits and the permuted-null; the observed edge must
    clear the **max** of the three (they measure the same quantity at
    different rigor levels — the sign-flip estimate is essentially a
    ±1-randomized permuted-null over the class rather than the procedure).
11. **CUSUM event filter + Chu-Stinchcombe-White break monitor** (cheap,
    closed-form critical values b₀.₀₅ = 4.6) for the monitoring leg; full
    SADF only where O(T²) is justified.
12. **Time-series (block/weighted) split-conformal intervals** on belief-card
    forecasts feeding human decisions (exchangeability breaks under serial
    correlation — the same failure and same blocking fix as permutation
    tests).
13. **FFD fractional differentiation** (ω recursion, fixed-width window,
    minimum d* passing ADF) as a feature-engineering standard before any ML
    candidate generation.

## 4. Crosswalk — shelf doctrine vs the built stack

| Shelf prescription | Status in Project_money |
|---|---|
| Record every trial; deflate by trial count (de Prado "Third Law") | **Built** (ledger) + **corrected** (DSR now takes the ledger's SRs) |
| Purged/embargoed CV; interval-overlap purge rule | **Partial** — walk-forward purge/embargo built; audit vs the exact 3-condition rule + note embargo is unnecessary in pure WF |
| CPCV path distributions; PBO | **Not built** — items 7–8 |
| Backtest is for discarding, never tuning | **Doctrine held** (cascade + firewall); books confirm verbatim |
| Blocking under serial dependence (bootstrap/permutation/conformal) | **Built** (block permutation) + estimator correction queued (item 4) |
| Never select and evaluate with the same estimate | **Partial** — maker≠checker holds at role level; fold-level split queued (item 3) |
| Calibrated (measured) confidence, never verbalized | **Queued** (item 6); judge protocol hardened now |
| LLM-judge never a sole gate; identity pinned; biases controlled | **Built + hardened this change set** |
| Constrained decoding for closed label sets | **Queued** — layering over the existing hook/schema validation |
| Untrusted-text ingestion defenses before sentiment work | **Documented prerequisite** (§5) — gate for the H12/S3 hypothesis families |
| VPI > cost as the review-routing trigger | **Queued** (needs payoff structure on belief cards) |
| 5-element spec grammar for hypothesis registration | **Adopt in MVP spec template** (documentation) |

## 5. Foundations for subsequent uploads (LLM-engineering prerequisites)

Before any news/sentiment/NLP hypothesis family is tested, the ingestion path
must have: (1) an untrusted-text boundary (retrieved text is data, never
instructions; sandwich framing; instruction-privilege rules; quarantine for
instruction-like content); (2) an input guardrail (injection-pattern screen;
no generated code/queries from ingested text executed without human
approval); (3) constrained-output classifier interfaces (closed label
vocabularies at generation time + schema validation); (4) temporal
contamination control for text (timestamps mandatory; n-gram-overlap dedup
between calibration and evaluation text; never resample before the temporal
split); (5) the few-label classifier ladder (zero-shot NLI with multi-wording
aggregation → embedding-kNN with exemplar provenance recorded in
evidence_records → fine-tune at ≳50–100 labels per class); (6) hybrid
retrieval + cross-encoder rerank as the independent relevance checker.
Slice-based evaluation (per-regime/per-sector) and
evaluation-before-building apply to every future component.

## 6. Housekeeping

- Sourcing debts (external to the shelf): Smith & Winkler (2006) for the
  shrinkage formula; Bailey & López de Prado (2012) for minTRL — both
  reconstructed by the agents, flag as external in any spec.
- The S&B duplicate PDF is byte-identical; deletion is the user's call.
- Corrected offsets table for future cites: de Prado +27, Powell +20, S&B
  +22, R&N +19, Murphy-Intro +30, Murphy-Adv +33, Mohri +17/+18,
  DasGupta +24, Huyen/Alammar/Tunstall unstable (navigate by headings).
