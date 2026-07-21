# Time-Series Forecasting Corpus Integration — batch 4 verification & extraction

> **Batch 4 of the information intake** (2026-07-21). Corpus: 26 PDFs in
> `~/Documents/Papers on Time Series Forecasting/` — the source literature
> behind the playbook's **v2.1 forecasting layer** (six policy docs in
> `~/Projects/decision_systems_playbook/docs/`), which Project_money has
> **deliberately not adopted** (STATE.md non-goals). Method: five
> verify-and-extract agents over exclusive clusters (LTSF transformers;
> linear/MLP critique; foundation/LLM; representation/graph/exogenous;
> benchmarking/meta), each verifying the playbook's claims against the actual
> papers page-by-page and extracting implementation-grade specs. Research-only
> throughout; nothing here authorizes the forecasting layer, providers, or any
> action. Claims below carry the fleet's page cites; per-paper detail lives in
> the agent digests (provenance in §6).

## 1. Verdict

**The v2.1 forecasting layer survives its source audit — with one hard defect,
one cross-doc inconsistency, and a set of wording/attribution corrections that
should be applied before adoption.** Across ~60 verified claims spanning all
six policy docs, no fabricated number, reversed ordering, or misattributed
result was found. This is the playbook's third successful independent audit
(after the batch-1 paper-map cross-check and the batch-3 ML-shelf pass).

The deeper result: **this corpus is a live demonstration of our doctrine, run
by the ML community on itself.** Informer's and Autoformer's SOTA claims
collapsed when a one-layer linear model was finally included (Zeng et al.);
the shared Informer/Autoformer codebase carried a real `drop_last=True`
test-set bug that understates error by up to ~17% MAE (TFB, measured); and on
the only genuinely financial series these papers touch, simple models win —
DLinear 0.643 and naive Repeat 0.823 MSE vs every transformer ≥ 1.195 (and vs
N-HiTS 0.798) on Exchange-720, VAR beating every recent deep SOTA on NASDAQ
(TFB Table 1), NLinear singled out on NYSE's severe drift (TFB §5.2.3). Zeng
attributes the failure of longer look-backs on Exchange to the "low
information-to-noise ratio" of financial data — precisely our regime.
**Baselines-as-nulls is hereby upgraded from doctrine to externally evidenced
finding** (still `research_only`; it gates nothing by itself).

The corpus also confirms the deferral it might have tempted us to lift: none
of the 26 papers evaluates on equity/ETF *returns*; every headline win lives
on high-SNR, strongly periodic data; and every LTSF paper reports
best-validation test error with **zero multiplicity correction** — below our
deflated-Sharpe bar. The ML/forecasting deferral stands on stronger ground
than before.

## 2. Verification results — defects and corrections for the v2.1 layer

These are **adoption prerequisites**, recorded here because the playbook is a
separate repo under its own governance. Patching it is a user decision
(§6 Housekeeping).

### 2.1 Hard defect

| # | Location | Defect | Fix |
| --- | --- | --- | --- |
| D1 | `probabilistic_forecasting_policy.md` §intro | **Time-LLM listed as an integrated probabilistic-forecasting source; it is point-only** (MSE objective, no quantiles/intervals/densities — Jin et al. pp. 3, 6, page-verified). | Drop Time-LLM from that list or re-scope its contribution to prompt/reprogramming design. |

### 2.2 Cross-doc inconsistency

| # | Location | Issue | Fix |
| --- | --- | --- | --- |
| D2 | `forecast_benchmark_policy.md` §4 vs `time_series_forecasting_policy.md` §2 | Benchmark policy orders statistical (ARIMA) **before** linear/DLinear; the hierarchy makes DLinear **Level 1** below ARIMA at **Level 2**. The two docs disagree on which is the earlier null. | Reconcile; the papers do not adjudicate an ARIMA-vs-DLinear head-to-head. |

### 2.3 Taxonomy / wording corrections (each page-verified)

| # | Location | Issue |
| --- | --- | --- |
| W1 | hierarchy §2 hard rule | Reads as a performance ladder, but **Level-3 TiDE routinely beats Level-4 N-HiTS** (Das Table 2). Restate as: "must beat the *nulls* (Levels 0–2)," not "each level dominates the one below." |
| W2 | hierarchy §2 Level 1 | **NLinear is last-value normalization, not decomposition** (Zeng App. D.1). |
| W3 | hierarchy §2 Level 4 | Autoformer is attention-based and single-scale — mis-grouped with MLP multiscale models; DLinear (L1) beats it decisively. |
| W4 | hierarchy §2 Level 3 | TFT is LSTM+attention, not a "dense" model; "interpretable covariate" is the accurate half. |
| W5 | hierarchy §2 Level 7 | "LLM-adapted" over-applies: **TimesFM/Toto/MOIRAI are trained from scratch on time-series data** (TimesFM p. 2 explicitly); only Time-LLM/LLMTime are LLM-adapted. Split the label — the two mechanisms fail differently. |
| W6 | §3 method-selection | "Transformer / channel-dependent" conflates two independent axes (PatchTST and PITS are channel-independent transformers/MLPs). The CD/CI binary is also oversimplified: **TimeXer's result is that a hybrid dominates either pure choice**, and DLinear beats all transformers on the highly *seasonal* Traffic/Electricity (Zeng Table 2), so the heuristic needs a scope condition. |
| W7 | §3 method-selection | **TFB vs QuitoBench source conflict**: TFB (incl. financial data) → linear wins on trend/shift; QuitoBench (high-structure telemetry) → DLinear ranks 8/10, wins zero regimes. Neither is wrong — different regimes. State the rule with its data-regime scope; for our low-SNR domain, TFB's side is operative. |
| W8 | `universal_forecasting_policy.md` §3 | "Quantile heads and CRPS matter" must never drift into "Toto is CRPS-trained" — **Toto trains with pinball loss; CRPS is the eval metric only** (Khwaja pp. 4, 10). Add the parenthetical. |
| W9 | `universal_forecasting_policy.md` §2–3 | Two claims stated as settled that the sources support only partially: MOIRAI's random context/horizon sampling has **no dedicated ablation**, and Toto's "scaling works *only under* a coherent recipe" asserts necessity from a single existence proof. Soften both. |

### 2.4 Attribution gaps (completeness, not falsity)

- `forecast_benchmark_policy.md` credits everything to "TFB lessons," but
  macro/micro dual aggregation, regime-balanced stratification, the
  forecastability axis, and the direct/indirect leakage-channel taxonomy are
  **QuitoBench** contributions the playbook never cites. Add the citation
  (with the provenance caveat: QuitoBench is a preprint on a proprietary
  single-vendor corpus — its *protocol* stands on its own; its *rankings* are
  `validation_pending`-grade).
- Three prescriptions — foundation-models-last ordering, calibration summary,
  abstention on low forecastability — are supported by **neither** benchmark
  paper. They are fine as doctrine; label them as doctrine, not as sourced.
- `time_series_representation_policy.md` bills "TS2Vec **and PITS** lessons"
  but states no PITS-specific finding. The missing PITS lessons are
  on-doctrine and worth adding: patch-independence beats patch-dependence,
  PI is more robust to distribution shift, and a ~6k-parameter MLP matches a
  400k-parameter Transformer.
- Informer and the Wu-Google influenza paper are cited nowhere in the layer —
  acceptable, but see the identity note in §6.

## 3. What the corpus establishes (evidence relevant to Project_money)

### 3.1 The linear-null result transfers to finance better than anything else

Convergent, independently sourced evidence — the strongest cross-cluster find
of the batch:

- **Zeng et al. (checker-verified figures, Exchange-720, MSE):** naive
  Repeat **0.823** and DLinear **0.643** beat every transformer (FEDformer
  1.195, Autoformer 1.447). NLinear is *weaker* on this cell (1.033) — which
  simple null wins varies by series, itself an argument for a multi-model
  null cascade rather than a single favorite. Transformers' apparent wins
  depend on a short fixed look-back (their error does not improve with more
  context; linear's does).
- **Challu et al. (cross-paper check, checker-verified):** N-HiTS
  Exchange-720 = 0.798 — better than every transformer, but **beaten by
  DLinear (0.643)**: a strong deep model failing to beat a two-head linear
  model on the corpus's one financial series (it does beat Repeat 0.823 and
  NLinear 1.033 there).
- **Lai et al. (LSTNet):** on Exchange the linear AR bypass beats the full
  deep model, and removing it is the largest ablation hit — the linear
  component carries the model on financial series.
- **TFB (peer-reviewed, includes daily equity data; checker-verified):** VAR
  0.462 MAE beats PatchTST 0.567, NLinear 0.522, FEDformer 0.547 on
  **NASDAQ** (Table 1); NLinear singled out for **NYSE**'s severe drift
  (§5.2.3/Fig. 8 — a selected-methods comparison, not a full-table "best").
  LR/RF top the univariate ranks overall.

Implication: on daily equity/ETF panels, **a Repeat/Linear/DLinear/NLinear
cascade is the model to beat**, and complex architectures mainly add
overfitting surface. Which member of the cascade wins varies by series
(DLinear on Exchange-720; NLinear on NYSE drift; Repeat beats all
transformers on Exchange) — so the cascade is run as a set, never a single
champion. This hardens the batch-2 decision that Tier-1 baselines (H1–H3)
become the null every later hypothesis must beat.

### 3.2 The corpus's own evaluation failures validate our verifier design

- **Drop-last is real and quantified**: batch-size-dependent test-set
  truncation understates PatchTST's MAE by up to ~17% (TFB Table 2); TiDE
  independently documents a PatchTST dataloader bug flipping ETTh1/h2
  comparisons. Rankings flip on plumbing — the reason our evaluation cascade
  recomputes metrics from artifacts.
- **Selection-on-noise at field scale**: Informer/Autoformer's headline SOTA
  (32/32 win cells; "38% improvement") did not survive the first linear
  baseline. Aggregate-average reporting hid regime-conditional failure
  (QuitoBench: a majority-regime specialist "fails silently on remaining
  regimes").
- **The multiplicity gap is systemic**: every LTSF paper reports
  best-validation test error with no multiplicity correction, no deflated
  metric, no economic-significance layer. Importing any of these models means
  adding our DSR/ledger discipline on top; the papers provide none.

### 3.3 Foundation/LLM forecasters: benchmark candidates at most

- Every foundation model loses to something simpler somewhere: TimesFM
  trails tuned seasonal-ARIMA and LLMTime on Darts (within statistical
  significance, per the paper); MOIRAI < TiDE/DeepAR on Walmart/Istanbul/
  Electricity; ChronosX 4th on MASE behind NBEATSx/NHiTS/PatchTSTx.
- **Contamination is pervasive and mostly under-defended**: TimesFM pretrains
  on Electricity/Traffic/Weather (and has an unreconciled traffic-hourly
  overlap); MOIRAI's Monash numbers are in-distribution, never zero-shot;
  LLMTime's defense is three post-cutoff series; Toto's recipe was tuned on
  GIFT-Eval validation and its flagship benchmark is home-field. Any future
  zero-shot number we cite must pass a per-model vintage/disjointness check.
- **In-principle limit**: zero-shot forecasters exploit exactly the structure
  (seasonality, autocorrelation, stable cross-series relations) that
  arbitrage removes from returns. Their honest role on our panels is a cheap
  probabilistic benchmark candidate gated *below* the naive nulls — exactly
  where the playbook already places them. LLM-based forecasters (Time-LLM,
  LLMTime) are additionally disqualified operationally by MDL/low-complexity
  doctrine (a 7B model at inference for a point forecast a ~1M-param linear
  model also yields).

### 3.4 Selectively transferable ideas (each with its trap)

- **NLinear-style last-value normalization** — the single most
  finance-relevant import (distribution-shift handling ≈ RevIN-lite). Trap:
  any instance normalization must use look-back-window statistics only.
- **Quantile/pinball outputs (TFT: P10/P50/P90 + q-Risk)** — distribution-free
  interval output validated on realized volatility of 31 stock indices. Trap:
  validated on *volatility* (clustered, forecastable), not returns; edge over
  strong baselines was single-digit percent.
- **iTransformer's cross-sectional variate attention** — the one architectural
  idea with a real economic rationale (factor structure). Trap: assumes a
  fixed variate universe and stable correlations; both false in equities
  (survivorship, regime shifts).
- **TimeXer's variate-token exogenous pattern** — built for exactly the
  irregularities macro data has (frequency mismatch, misalignment); the
  natural pattern for H3 volatility-state conditioning if a conditioning
  model is ever justified. Traps: macro usable only as of *release* timestamp;
  and its robustness result cuts both ways — if macro conditioning "helps" a
  lot on daily returns, suspect leakage before believing it.
- **PITS as evidence, before PITS as a model** — a ~6k-param patch-wise MLP
  matching a 400k-param Transformer supports simplicity-first from inside the
  DL literature; usable later as a cheap Level-5 null.
- **TS2Vec masked-vs-unmasked representation distance** — an anomaly/quality
  flag routing to `needs_human_review`; explicitly non-authority. Its
  ablations also show imported augmentation invariances (jitter/scaling/
  permutation) *hurt* — "invariances don't transfer for free."
- **Do not build**: MTGNN-style freely learned stock graphs (an `O(N²)`
  multiplicity minefield; its own paper fails on Exchange-Rate, its only
  finance-like series), ProbSparse/Auto-Correlation/distilling (periodicity-
  premised efficiency tricks), LLM forecasters (above).

### 3.5 SSL/pretraining leakage vectors (catalogued for any future use)

1. Encoder pretraining span crossing the OOS window → silent lookahead in
   every downstream feature; walk-forward re-fit required.
2. Full-series normalization statistics (RevIN/per-series) → direct leakage;
   causal (expanding/rolling) stats only.
3. Cross-sectional contamination via instance-wise contrastive negatives
   (contemporaneous panel info bleeding into per-name representations).
4. Third-party pretrained artifacts with undeclared training cutoffs →
   vintage check or tracked verification debt (see V3 below).

## 4. Consolidated build list

### 4.1 Verifier additions — worth building regardless of any forecasting decision

Ranked; these extend the *existing* backtest verification backbone. They join
the batch-3 follow-on list (`ml_shelf_integration.md` §3) in the sequencing
queue; none blocks the current gates.

| # | Item | Source | Sketch |
| --- | --- | --- | --- |
| V1 | **Window-completeness assertion** (anti-drop-last for backtests) | TFB pp. 3, 9 | Assert scored evaluation windows = expected count from declared stride; flag any count that varies with an engineering parameter (batch size, vectorization chunk). |
| V2 | **Equal-treatment protocol for candidate vs null** | TFB p. 8 | Identical splits, identical preprocessing, and a bounded *equal* hyperparameter budget for candidate and baseline, logged in the evidence record; asymmetric-budget comparisons cap at `validation_pending`. |
| V3 | **Pretrained-artifact vintage check** | QuitoBench p. 2 (Meyer et al. channels) | Extend the leakage/vintage auditor: any pretrained model/embedding used in a pipeline must carry a declared training-data cutoff strictly before OOS start; missing cutoff ⇒ tracked verification debt, never a silent pass. |
| V4 | **Effect-size gate** | QuitoBench p. 27 | Every significance claim carries an effect size (economic magnitude) beside p/DSR; "significant but negligible-d" results are labeled accordingly. Complements the batch-3 ROPE item. |
| V5 | **Macro/micro dual aggregation** | QuitoBench §2.2 | Report pooled and per-regime results; passing only the pooled number fails the gate (prevalence-skew guard). |
| V6 | **Threshold-sensitivity sweep** | QuitoBench E.5 | Any binarized gate/label sweeps its threshold and requires ranking stability. |
| V7 | **Cross-metric ranking stability** | QuitoBench p. 28 | Conclusions must hold under ≥2 performance metrics. |
| V8 | **Forecastability diagnostic** | QuitoBench pp. 16–17 | Per-series spectral-entropy forecastability as a standing SNR proxy feeding confidence/abstention language in findings. |

### 4.2 Fleet-operations updates (from AIRS-Bench, relates to batch 1)

- **Valid-output-rate tracking**: ~45% of AIRS-Bench agent runs failed to
  produce a valid submission; count schema-invalid findings as a fleet health
  metric rather than silently retrying.
- **Enforcement must be environmental, not prompt-layer**: their
  contamination control was an agent-flippable env var. Confirms our
  hook/sandbox approach (fail-closed hooks, read-only roles) over
  instruction-only constraints — already our practice, now externally
  evidenced.
- **Goodhart warning made concrete**: where agents beat human SOTA they did
  it by optimizing the stated metric hard (ensembles, OOF CV). In our domain
  the metric is a backtest; the skeptic/red-team role is load-bearing, not
  optional.
- **Metric-transform sensitivity**: any composite score used to rank
  candidates must be reported under ≥2 transforms (their own task-difficulty
  ranking reorders between transforms).
- Best-of-N + multi-seed over one-shot confirmed (aligns with
  trajectory-judge practice and its n≈20 authority limit).

### 4.3 If the forecasting layer is later authorized (pre-specified, gated)

1. **Null cascade, exact specs**: Repeat; Linear (`W ∈ ℝ^{T×L}`, shared,
   direct multi-step); DLinear (moving-average kernel 25, two linear heads);
   NLinear (subtract/re-add last value). All ~10⁵ params, CPU-cheap,
   deterministic — the mandatory floor for any model class.
2. **Evaluation protocol**: global shared temporal cutoff across the panel;
   dense rolling windows with declared stride **plus HAC/block-bootstrap
   inference** (overlapping-window errors are autocorrelated — do not import
   QuitoBench's exchangeability assumption); look-back × horizon grid, never
   a single fixed context; scale-free metrics (MASE/WAPE) plus the economic
   layer; rank-first-then-average across series; multi-seed with spread.
3. **Probabilistic output**: pinball-trained quantile head (P10/P50/P90,
   q-Risk) with actual calibration diagnostics (PIT/coverage) — none of the
   papers provide them for finance.
4. **Series characterization module**: TFB's six characteristics + QuitoBench
   forecastability, computed per series before any method selection.
5. Foundation models strictly as contamination-checked benchmark candidates
   below the nulls (per-model checks in §3.3); ChronosX-style covariate
   injection only IIB (past-covariate), frozen, small.
6. TimeXer-pattern macro conditioning for H3 only behind a pre-registered
   economic prior and release-timestamp lagging; cheaper regime-gating first.

## 5. Crosswalk and ungating impact

- **Batch 1 (agent tooling):** AIRS-Bench closes the loop on "the verifier is
  the product" — an industrial maker≠checker harness whose agents beat SOTA
  only by metric optimization, i.e., the exact failure our promotion gates
  exist to catch. Fleet-ops items (§4.2) extend that synthesis.
- **Batch 2 (trading corpus):** the linear-null evidence (§3.1) hardens the
  Tier-1-baselines-as-nulls plan for H1–H3; TFB's NASDAQ/NYSE results are the
  first peer-reviewed, equity-specific external support for it. The
  delisting-aware panel requirement is unaffected.
- **Batch 3 (ML shelf):** the multiplicity gap (§3.2) is the same gap the
  DSR correction addressed; V4 complements ROPE; V3 extends the
  vintage/leakage auditor exactly along its existing axis. The batch-3
  follow-on list and §4.1 merge into one sequencing queue when validation
  work resumes.
- **Ungating impact: sharpens, does not reorder.** The agreed (unrecorded)
  1–4 plan stands. This batch adds: adoption prerequisites for the v2.1 layer
  (§2) if forecasting is ever authorized (item beyond the current 1–4), the
  §4.1 verifier queue, and stronger evidence that the ML/forecasting deferral
  is correct (baselines first — now externally evidenced). Ungating remains
  recorded **only on the user's end-of-information signal**.

## 6. Housekeeping

- **Provenance**: five verify-and-extract agents (2026-07-21), exclusive
  clusters over the 26 PDFs, page-cited verdicts throughout; full digests in
  the session transcript. **An independent checker then spot-checked ten of
  this document's headline claims against the primary sources: 8 confirmed;
  2 corrected** (a reading-agent digest had mixed MSE/MAE columns on Zeng's
  Exchange-720 row and inverted one cross-paper comparison — fixed above;
  lesson recorded in `tasks/lessons.md`). Load-bearing figures in §1/§3.1
  are restricted to checker-verified cells. Playbook docs audited:
  `time_series_forecasting_policy.md`, `forecast_benchmark_policy.md`,
  `probabilistic_forecasting_policy.md`, `universal_forecasting_policy.md`,
  `time_series_representation_policy.md`, `forecast_input_taxonomy_policy.md`.
- **Identity note (citation hygiene)**: "Deep transformer models for time
  series forecasting_Wu et al..pdf" is the **Google influenza-nowcasting
  paper (Neo Wu et al., 2020)**, not Autoformer (Haixu Wu et al.). Two
  different "Wu et al." — never conflate. Filename↔identity map for the rest
  confirmed by the fleet.
- **Upstream corrections**: §2's defects are in the *playbook* repo
  (`~/Projects/decision_systems_playbook`), which this project does not own.
  Whether to patch it there is a user decision; until then, §2 is the
  adoption-prerequisite checklist.
- **Status discipline**: everything in this document is `research_only`
  synthesis; the corpus's empirical claims enter our knowledge base as
  evidence-tiered inputs (peer-reviewed TFB/AAAI/ICLR/NeurIPS/KDD sources vs
  preprint QuitoBench/Toto), and nothing herein promotes any hypothesis or
  authorizes any capability.
