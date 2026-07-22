# Stock-Market ML/AI Corpus Synthesis — batch 6 (final intake)

> **Batch 6 of the information intake — the FINAL batch** (2026-07-22, user-declared
> end-of-information). Corpus: 73 files in `~/Documents/PWC_stock_market_papers/` —
> LLM trading agents and live benchmarks, market simulation and microstructure,
> formulaic-alpha mining, RL trading/portfolio, bespoke stock-prediction
> architectures (transformer/GNN/MoE/memory), financial NLP and datasets, causal
> discovery / model-validity / conformal, and two generic-deep-learning sweeps.
> This is our **direct domain** and, as predicted, the **highest junk-density corpus
> of the whole intake**. Method: eight adversarial-triage reading agents over
> exclusive clusters, run as a resumable Workflow (the third attempt after two Fable
> runs died on spend/credit limits mid-fan-out), each cluster's load-bearing numeric
> claims independently verified against the PDFs inside the pipeline. Research-only
> throughout; ML, providers, and every execution path remain gated. `[F]`=fact,
> `[PC]`=paper-claim, `[A]`=assessment carried through from the digests.

## 1. Verdict

**Across 73 papers in our own domain, not one demonstrates a tradeable
daily-horizon edge that survives honest nulls, honest out-of-sample evaluation,
and transaction costs simultaneously.** That is the strongest possible
confirmation of the doctrine assembled over batches 1–5: in the literature most
incentivized to show ML beating markets, the honest evaluations produce negative
or null results, and the impressive-return papers are the contaminated ones. The
corpus's value is therefore threefold and none of it is a strategy: (1) a **large,
concrete verifier/policy upgrade** — the highest-yield methodological haul of the
intake, because in-domain junk exposes in-domain failure modes; (2) the
**definitive contamination case** — DeepFund's peer-reviewed "time-travel"
benchmark shows 8 of 9 LLMs losing money under leakage-free live evaluation; and
(3) a **dataset catalog** for the eventual provider-ungate era, tagged for
vintage-safety.

Triage outcome: **CREDIBLE 10 · PARTIAL 23 · JUNK 33 · OTHER 7** (73 total). The
10 "credible" papers are credible **as methods or as correctly-scoped findings —
none is a validated tradeable edge** (this distinction is load-bearing and is kept
explicit throughout). Independent verification checked **57 load-bearing claims →
52 CONFIRMED, 5 CONFIRMED-with-correction, 0 REFUTED, 0 could-not-locate** — the
cleanest checker result of any batch, with the corrections all minor
(table-label imprecisions, a comparator-column mixup, a best-baseline swap) except
one substantive walk-back recorded in §6/§12.

## 2. The corpus by the numbers

| Cluster | CRED | PART | JUNK | OTHER | The one thing to remember |
| --- | --- | --- | --- | --- | --- |
| LLM trading agents & live benchmarks | 3 | 5 | 3 | 1 | DeepFund (NeurIPS'25): 8/9 LLMs lose live; S&P −6.91% over the window |
| Market simulation & microstructure | 2 | 0 | 4 | 0 | Sirignano–Cont: deep beats linear at **next-tick** (not daily returns) |
| Factor mining, RL trading & portfolio | 1 | 4 | 4 | 1 | Alpha Jungle's Table-5 known-zero LLM control (search, not memory) |
| Stock-prediction architectures | 0 | 6 | 6 | 0 | Stockformer's own **LightGBM null wins** the uptrend backtest, net of costs |
| Financial NLP & datasets | 1 | 2 | 6 | 1 | EDT: event-news edge **evaporates within one minute** of publication |
| Causal, validity & conformal | 3 | 1 | 1 | 3 | "Has the DNN learned the process": our harness lacks a **calibration axis** |
| DL-stocks pathology sweep A | 0 | 2 | 6 | 0 | Intra-bar OHLC leakage → 94.76% "OOS" accuracy our detector would pass |
| DL-stocks sweep B + tooling + misc | 0 | 3 | 3 | 1 | FinWorld bundles execution paths — out of scope wholesale |

## 3. What survived as credible (and what it actually says)

None of these is a daily-horizon alpha. Each is credible as a method, an
exemplar, or a correctly-scoped negative:

- **DeepFund — "Time Travel is Cheating" (NeurIPS 2025 D&B).** The flagship for our
  doctrine. Leakage-free live-forward evaluation (trading window post-dates every
  model's pretraining cutoff): only 1 of 9 LLMs positive (+1.1%), 8 negative to
  −8.1%, S&P −6.91%; 8/9 underperform their *own* buy-and-hold. Verified exactly.
  The single anti-contamination mechanism is **temporal separation**, and it is
  sufficient for a truly live feed.
- **Nexus (Google DeepMind).** A leakage-aware agentic forecasting framework
  (strictly post-cutoff evaluation; calibration by fold-rule intersection + a
  hidden-validation gate). Credible **as a method**; its gains on stocks are tiny
  (~1.2% MAPE over chain-of-thought) and it omits the naive random-walk null —
  itself doctrine-consistent: elaborate agentic reasoning barely helps on low-SNR
  equities.
- **AI Analyst (JPMorgan).** Not a trading claim — LLM financial-report generation.
  Credible for its cautions: LLM-as-judge is a weak proxy for factual grounding
  (Spearman ρ=0.33 on consistency vs human experts), and it observes the
  contamination mechanism directly (factual consistency drops and hedging rises for
  data past the training cutoff). Feeds S30 and the contamination doctrine.
- **Sirignano–Cont, "Universal features of price formation" (2018).** A genuine,
  honestly-evaluated case where deep beats linear: one LSTM trained on the pooled
  cross-section predicts the **next mid-price move** at ~65–70% on completely
  unseen stocks (25/25 held-out), stable 18 months out. **Boundary condition, not
  a contradiction:** it lives at ~1.7-second event-time (high-SNR, N in the
  billions, order-flow-imbalance-driven), with **no P&L, no costs, no spread**, and
  says nothing about daily-return predictability. Deep beats linear precisely where
  our regime is not.
- **TradeFM (JPMorgan, 2026).** A generative order-flow simulator, from-scratch +
  strict temporal holdout (train ≤Dec-2024/test ≥Jan-2025) — the *correct* answer
  to batch-4's "foundation models are candidates, contamination-checked." Validated
  only on distributional realism (2–3× lower K-S than a Compound-Hawkes null; and
  honestly reports Hawkes *beating* it on bid-ask spreads). Not a return predictor.
- **Alpha Jungle (2025).** Factor mining with the batch's best discipline: OOS +
  costs + a real **known-zero LLM-contamination control** — directly prompting
  GPT-4.1/Gemini/DeepSeek for CSI300 formulas yields IC 0.013 ≈ random 0.0126,
  while the search yields 0.053. Proof the LLM holds no memorized edge; the search,
  not memorization, produces the signal. Edge is modest (RankIC ≈0.04),
  single-window, and undeflated for search multiplicity.
- **Scherrmann Multi-Label Topic Model (LMU).** The one paper a staff quant would
  sign: rigorous event study (market model, firm+year FE, clustered SE, n=29,143),
  honest framing (contemporaneous *reaction*, e.g. Bankruptcy-Filing −16.02pp, not
  a forecast). Extract the reaction/forecast distinction, not an edge.
- **CD-NOD (JMLR 2020).** Causal discovery under nonstationarity: a surrogate
  time/domain index turns regime shift into *information* that identifies structure
  and change-points (its stock change-points align with the 2008 crisis / TED
  spread). Credible **as a method**; its market results are explicitly qualitative.
  A candidate for the future regime/structural-break layer, never a return forecast.
- **"Has the DNN Learned the Stochastic Process?" (ICLR 2025).** Names the single
  verifier gap of the batch: Expected Calibration Error is a *necessary* condition
  for fidelity to the data-generating process and is the only common metric
  (vs AUC-PR/MSE/BCE/CRPS) that isolates it from a single realization. Our harness
  has **no calibration/process-fidelity axis** (see §6).
- **Decomposition-Based Modular Conformal Prediction (ICML 2026).** The
  batch-3-queued conformal item, spec'd: split-conformal's coverage holds only
  under exchangeability (which time series break); the paper supplies a φ-mixing
  relaxation, an adaptive (ACI) long-run-coverage variant, and — valuable for us —
  a **diagnostic abstention** (empty valid set ⇒ emit no interval), which maps onto
  our `needs_human_review` label.

Two **PARTIAL-tier** papers (not counted in the CREDIBLE 10) also supplied
load-bearing extraction inputs and are noted here so they aren't mistaken for
tradeable results either: **AlphaGen (KDD'23, PARTIAL)** — its Table 3 shows two
alphas with mutual IC 0.9746 combining synergistically and a near-zero-IC alpha
(0.0011) being load-bearing, the evidence behind the combination-level redundancy
screening in §7; and **VTA / Reasoning-on-Time-Series (ICLR 2026, PARTIAL)** — a
serious method with an honest scoping negative (verbal TA reasoning helps only
where intrinsic interpretable signals exist), whose performance numbers are
marginal-over-best-baseline and contaminated, so we adopt the method idea (gated)
and its blind-expert-eval design, not the numbers.

## 4. The central negative result and the "would-be real news"

Every candidate that looked like it might beat an honest null failed on
inspection — and each failure is itself a catalogued specimen:

- **AI-TRADER US market:** MiniMax-M2 9.56% / DeepSeek 8.39% vs QQQ 1.87%,
  contamination-controlled — but no costs, ~5-week window, n=1, and the *same
  agents lose to their nulls in A-shares and crypto*: the signature of a lucky
  draw, not durable alpha.
- **Stockformer (architectures):** the only paper with walk-forward + costs + GBDT
  nulls — and its own **LightGBM null wins the uptrend backtest (270.45% / Sharpe
  9.12 vs the transformer's 239.73% / 8.46)** while showing *negative* predictive
  IC. The strongest in-domain confirmation of baselines-as-nulls in the intake,
  plus a metric-falsification specimen (IC and return decoupled).
- **Mehtab & Sen Case III (sweep A):** 94.76% "OOS" directional accuracy — a
  **contemporaneous intra-bar OHLC leakage** artifact (same-slot high/low/close
  predicting the same slot's open-return). The single most valuable specimen,
  because our bar-granularity lookahead detector would **pass it** (§6).
- **When Agents Trade / AMA:** "LLM agents trade profitably, surpassing
  buy-and-hold" — annualized from a 2-month, single-path, 4-asset window (SR 6.47).
  Statistically vacuous; directly contradicted by DeepFund and STOCKBENCH.
- **FinWorld:** DL>GBDT and RL-best (101.55% ARR TSLA) — cherry-picked
  single-window maxima across a large grid with no DSR, likely under-tuned GBDT
  nulls, and contaminated LLM-agent trading. Defeated by our DSR gate +
  baseline-parity audit + contamination gate acting together.

The honest positives are all negatives: EDT's own Table 5 (event-news edge dies in
<1 minute), the Li/EIIE thesis (a celebrated DRL portfolio agent **converges to
1/N** on equities), and Nabipour's R²≈1.0-at-every-horizon (a leakage fingerprint).

## 5. Verifier & policy build list

The batch's real yield. These join the batch-4 **V1–V8** and batch-5 **W1–W6**
queues in one sequencing pool. Items are grouped; each names the specimen(s) that
motivate it. "S-" numbering is this batch's additions.

### 5.1 Contamination & vintage (extends batch-4's mandatory contamination check)

| # | Item | Motivating specimens |
| --- | --- | --- |
| S1 | **`frozen_at` + strictly-post-timestamp forward tracking** for every paper-candidate — only bars strictly after the freeze count toward tracked hypothetical return. The loop-native, provable anti-look-ahead control. | DeepFund, STOCKBENCH, AI-TRADER |
| S2 | **Model/embedder pretraining-cutoff registry → contamination-by-default label**, extended to **LLM-derived features/labels** (not only zero-shot predictions): any feature generated by a model whose training cutoff post-dates the feature timestamp is auto-`validation_pending`. | GPT-InvestAR, QLoRA, FinSen (FinBERT on 2007 news), TwinMarket, ASFM |
| S3 | **Model-vintage gate**: reject or cap at `research_only` any pretrained-model result where training cutoff ≥ eval-window start. | TwinMarket (GPT-4o knows the 2023 SSE-50 it "predicts"), MarketSenseAI ×2 |

### 5.2 Nulls, metrics, and the leakage detectors (the GAPS are here)

| # | Item | Motivating specimens |
| --- | --- | --- |
| S4 | **Mandatory persistence/random-walk null as rung-0** of every forecast evaluation; a candidate that does not beat it OOS is auto-`reject`. The universal defect — not one of ~30 forecasting papers ran it. | all sweep papers, FNSPID, Social-Media-Exec |
| S5 | **Returns-not-levels metric policy** + auto-flag R²>0.95 on price levels and corr/R²≈1.0 on returns; **level-lag detector** (ŷ_t ≈ y_{t−1}). | FNSPID (R²=0.988), Robust-DL (corr 1.00), ResNLS, Hybrid-LSTM-GNN |
| S6 | **Intra-bar / contemporaneous-leakage detector** (feature-availability-time vs target-decision-time at *sub-bar* granularity). **GAP — highest-value find:** a bar-granularity detector passes same-slot O/H/L/C features. | Mehtab & Sen Case III (94.76%) |
| S7 | **Non-causal signal-decomposition leakage class:** forbid EMD/EEMD/VMD/DWT/wavelet and correlation/covariance graphs unless provably fit train-only and applied causally per-window. **GAP** — purge/embargo walk-forward does not cover this. | ACEFormer, Stockformer (graph carries ~65% of IC, window unspecified) |
| S8 | **Non-causal feature-construction detector:** flag bidirectional interpolation, spline, global smoothing, global min-max scaling. **GAP.** | Social-Media-Exec (cubic spline ~97% interpolated), FNSPID (global min-max) |
| S9 | **Scaler-fit-train-only linter / normalize-before-split + shuffle-then-split red flags.** | Paper 8, CNN-LSTM (shuffled series), Analyst-Rating |
| S10 | **Horizon-monotonicity test:** OOS error must be weakly increasing with forecast horizon; flat/inverted curves are a leakage fingerprint. **GAP.** | Nabipour (R²≈1.0, flat error 1→30 days) |
| S11 | **Metric-sanity alarm:** auto-flag sustained OOS directional accuracy above a plausibility threshold (~60%) for a mandatory leakage audit. | Paper 8 (0.96–0.99), Sectoral LSTM (~0.98), Case III |
| S12 | **Minimum-track-record-length gate:** reject Sharpe/Sortino computed from windows too short to support them (deflated-Sharpe complement). | AMA (SR 6.47/2mo), AI-TRADER (SR 4.42/5wk), Stockformer (Sharpe 8–9/3mo) |
| S13 | **Volatility null ladder:** register HAR-RV + EWMA(σ) as mandatory nulls (with a realized-vol proxy, not RMSE-vs-return) for any σ-target. | Stock-Volatility (units-mismatch "LSTM beats GARCH") |
| S14 | **Cross-model scale/target-consistency assertion:** reject "A beats B" comparisons on different-scaled or different targets. | Stock-Volatility (LSTM RMSE 0.011 vs GARCH ~10) |
| S15 | **Matched-horizon protocol:** nulls and candidates forecast the same horizon. | Pilla & Mekonen (multi-step ARIMA vs 1-step LSTM) |

### 5.3 Costs, universe, evidence-quality

| # | Item | Motivating specimens |
| --- | --- | --- |
| S16 | **Transaction-cost + slippage gate:** minimum cost model = 0.1%/side + venue duty (Stockformer's convention); any cost-free profitability claim is at most `validation_pending`; turnover-aware. | every live benchmark, all backtests |
| S17 | **Mandatory 1/N (equal-weight) null in every portfolio evaluation.** | EIIE converges to 1/N; China-DRL's omission is disqualifying |
| S18 | **Universe-construction / forward-selection audit:** point-in-time constituents, no outcome-conditioned selection ("prefer historically up-trending stocks"). | China-DRL, Paper 8 survivorship, Analyst-Rating FAANG |
| S19 | **Baseline-tuning parity audit (maker≠checker):** a "DL beats GBDT/linear" claim requires the null tuned to parity; an implausible error gap is a red flag, not a win. | FinWorld (2.6× MAE gap), Stockformer neg-IC anomaly |
| S20 | **IC/return sign-decoupling flag:** require both IC and cost-aware return; flag disagreement. | Stockformer (LightGBM: neg IC, best backtest) |
| S21 | **Honest-null bar:** beating another (often contaminated, near-random) model is not evidence of edge. | QLoRA ("beat GPT-4" whose MCC=0.03) |
| S22 | **Importance-attribution guard:** "feature X matters" needs OOS predictive-contribution evidence, not PCA/variance loadings. | Analyst-Rating |
| S23 | **Feature-provenance / synthetic-data audit:** forbid features fabricated using label/outcome knowledge. **GAP.** | AIMM (synthetic social features encode the labels) |
| S24 | **Author/template + citation-cluster dedup:** N near-identical papers from one group count as ~1 evidence unit. | Sen/Mehtab (6 of 8 sweep-A papers; 3 are the same template on 3 stocks) |
| S25 | **Reaction-vs-forecast KB tag:** an event-study contemporaneous reaction is not tradeable alpha. | Scherrmann (−16.02pp reaction) |

### 5.4 New evaluation axes (not just checks — new dimensions)

- **S26 — Calibration / process-fidelity axis (ECE), highest-value new axis.**
  Implement reliability-diagram binning as a *necessary-not-sufficient* check run
  alongside point metrics. Heavy caveat carried from the source: the target
  statistic is unobservable from a single real price path, so this is first-class
  only where an ensemble can be constructed (block-bootstrap / resampled returns /
  cross-sectional pooling). (Has-the-DNN, ICLR 2025.)
- **S27 — Known-positive controls.** Add a "PINN-recovers-known-closed-form" control
  (a net trained to satisfy a solvable PDE must *match*, not beat, the analytical
  solution on held-out inputs), complementing our known-zero controls and batch-5's
  planted-signal W1. (Black-Scholes-NN, done correctly.)
- **S28 — Conformal intervals with abstention → `needs_human_review`** for research
  reports; use the φ-mixing/ACI variants on serial data, never vanilla split
  conformal. (ICML 2026; the batch-3 queue item.)
- **S29 — Rolling-k delta randomness probe** (freeze positions k periods ago; if
  delay doesn't degrade tracked performance, the "signal" is noise) and
  **regime-split reporting** (up/down) as default forward-tracking views.
  (LiveTradeBench, STOCKBENCH.)
- **S30 — LLM-judge is never the checker for facts** (ρ=0.33 vs human on
  consistency); an LLM judge is a maker aid only, factual verification stays
  deterministic. (AI-Analyst.)

## 6. The GAPS — failure modes our harness currently cannot catch

Consolidated, because these are the batch's most valuable output (a check we lack
is worth more than a specimen we already catch):

1. **Intra-bar contemporaneous leakage** (S6) — same-slot O/H/L/C predicting the
   slot's open-return; a bar-granularity detector passes it. Requires modeling
   intra-bar information-arrival order (open before high/low/close).
2. **Non-causal decomposition leakage** (S7) — EMD/DWT/wavelet and correlation
   graphs fit with test-window data; walk-forward purge/embargo does not see it.
3. **Non-causal feature construction** (S8) — global/bidirectional transforms
   (spline, smoothing, global min-max).
4. **Calibration / process-fidelity** (S26) — an entirely missing evaluation axis;
   a model can nail point-accuracy on one path yet be miscalibrated to the process.
5. **Synthetic-feature label leakage** (S23) — features fabricated with label
   knowledge.
6. **Horizon non-monotonicity** (S10) and **evidence-cluster inflation** (S24) —
   cheap structural checks we don't currently run.

**One proposed detector failed verification and is NOT adopted:** a
"pretrained-vs-from-scratch performance-gap alarm" (flag benchmarks where
pretrained-LLM forecasters cluster far above from-scratch models on pre-cutoff
data, as a contamination smell). The checker showed several *from-scratch* DL
models also reach ~0.07 MSE on StockNet, so low MSE is not a reliable contamination
signature — the clustering argument does not hold. The **model-cutoff-vs-test-window
gate itself (S2/S3) stands**; this particular heuristic does not. Recorded as a
lesson (§12 and `tasks/lessons.md`).

## 7. Search discipline (inputs to the future bounded search — ungating item 3)

From the two factor miners (Alpha Jungle, CREDIBLE; AlphaGen, PARTIAL), pre-registered for
if/when a bounded strategy/factor search is authorized:

- **Charge every *evaluated* formula/config to the ledger, not the paper's reported
  count** — neither miner cleanly reports its total evaluations; MCTS/PPO generate
  far more candidates than the final selected set. Our DSR must deflate by the
  evaluated-trial count (reinforces batch-5 **W4**).
- **Fitness ≠ scoring metric.** Both miners climb IC/RankIC; every RL portfolio
  paper that reports a Sharpe "win" uses Sharpe as the reward (Goodhart, batch-1).
  The reward must not be the evaluation metric.
- **Screen redundancy at marginal-OOS-combination-IC level, not pairwise
  correlation** — this **modifies our prior doctrine**: AlphaGen shows mutual-IC-0.97
  alphas combine synergistically and a near-zero-IC alpha can be load-bearing, so a
  naive correlation/MI dedup screen discards synergy. (Note the field disagrees —
  Alpha Jungle *uses* a max-corr<0.8 filter; we side with combination-level
  screening + DSR.)
- **Complexity-penalized OOS-decay stopping** — Alpha Jungle's IS−OOS gap widens
  with formula depth; prefer shallower formulas at equal OOS IC (MDL-aligned).
- **Dimensional-consistency grammar constraint** and **DSR-over-configs / best-of-N
  flag** (charge the k in "best of 9 configs").

## 8. Dataset catalog (for the provider-ungate era)

Cached point-in-time data is the substrate once providers ungate; these are
candidate resources, tagged for vintage-safety:

| Dataset | Contents / span | Release timestamps? | Verdict |
| --- | --- | --- | --- |
| **EDT** (Trade-the-Event) | US PR/news; 303,893 timestamped articles + 9,721 event-labeled; 2020–2021 | **Minute-level — VINTAGE-SAFE** | Event-study/latency corpus; strategies must survive its own <1-min latency test |
| **Trillion Dollar Words** (FOMC) | Fed minutes/speeches/pressers 1996–2022; hawkish/dovish labels | **Release-date aware — vintage-aware** (CC BY-NC 4.0) | FOMC macro feature; never the cost-free QQQ strategy |
| **Ad-Hoc Multi-Label DB** (Scherrmann) | 3,044 German ad-hoc announcements, 20 topics, 29,143 event obs | **Report-date — vintage-aware** | Sentence-level multi-label BERT pattern; German-only |
| **EDGAR 10-Ks** (via GPT-InvestAR) | ~24,200 US 10-Ks 2002–2023 | Filing-date — vintage-safe raw corpus | Raw text only; the paper's LLM scores are contaminated |
| **FNSPID** | 4,775 S&P500 firms, 1999–2023, 15.7M news + 29.7M prices | **DATE-only — VINTAGE-UNSAFE** (no intraday release time) | Large but can't tell pre/post-close; murky scraped license |

**Honest text-as-signal evidence (after controls):** event news carries a real but
**latency-bound** signal gone within ~1 minute (EDT Table 5: +1.74% at the open →
−0.07% at the close of the same minute); FOMC tone is economically real (CPI corr
0.54) but its trading edge is unproven; announcement topics explain
*contemporaneous* abnormal returns (reaction, not forecast); text→next-day
direction AUC caps at ~0.53–0.64; sentiment adds ~0.2% (FNSPID's own finding, which
led its authors to drop ChatGPT sentiment). Consistent with baselines-as-nulls.

## 9. Do-not-build ledger & the execution-adjacency boundary

The corpus is wall-to-wall trading systems; the boundary was reaffirmed in every
cluster and is restated here as the controlling constraint:

- **No order-placement / broker-execution / fund-movement path.** FinRL exposes a
  `Trade` action; AI-TRADER exposes an MCP `Trade` tool; TiMi runs live minute
  bots; FinWorld bundles an RL trading environment, RL/LLM trading trainers, and a
  "Deployment" pipeline; EDT and Paper 8 ship backtest-to-live-trading harnesses.
  **A capability existing is not authorization to build it** (CLAUDE.md §1–2, §7;
  safety_policy). We extract statistics, evaluation discipline, and datasets —
  never the trading machinery. Even the backtest simulators (TopK-Dropout rebalance,
  top-k buy/sell) are execution-*adjacent* and stay read/analyze-only.
- **Do-not-build:** LLM stock-picking backtested on pre-cutoff data (MarketSenseAI
  ×2 — contaminated by construction; keep as pathology fixtures); price-LEVEL
  forecasters (persistence-dominated); EMD/wavelet-denoised pipelines (leakage
  class); freely-learned stock graphs (batch-4/5 reaffirmed — MS-HGFN 53% ACC /
  MCC 0.06); loss-function-as-profit-metric training (Goodhart); RL portfolio
  agents as an edge source (converge to 1/N); ultra-short-window annualized-Sharpe
  benchmarking; undefined-metric ("accuracy" on price regression) evaluation; any
  LLM-agent trading backtest on pre-cutoff data as edge evidence.
- **Known-bad calibration specimens** to add to the falsification harness (the
  harness *must* reject each; a pass is a hole): Paper 8 (scaler-leak + zero-cost +
  survivorship + impossible accuracy), Mehtab-Sen Case III (intra-bar leakage),
  Nabipour (flat-horizon R²≈1.0), MarketSenseAI (time-travel), CNN-LSTM (shuffled
  split).

## 10. Crosswalk and the intake-wide conclusion

- **Batch 1 (agent tooling / Goodhart):** every RL portfolio paper that reports a
  Sharpe "win" uses Sharpe as its reward; Stockformer trains on the profit metric
  it reports. The skeptic role is load-bearing — confirmed in-domain.
- **Batch 2 (trading corpus / H1–H3 seeds):** unaffected; the datasets (§8) and the
  1/N + cost discipline serve the delisting-aware panel plan.
- **Batch 3 (ML shelf):** the queued conformal and CUSUM items are answered/advanced
  (S28); the DSR-multiplicity theme recurs (FinWorld cherry-picking; search trial
  counting).
- **Batch 4 (TS forecasting):** contamination-check mandate massively reinforced —
  DeepFund, AI-Analyst (consistency drops past the cutoff), Trillion Dollar Words
  (zero-shot ChatGPT loses and is correctly rejected as a baseline). Extended to
  LLM-derived *features* (S2).
- **Batch 5 (graph ML):** learned-stock-graph do-not-build reaffirmed on in-domain
  papers; MTMD gives direct support (exogenous concept graph HIST 0.131 > learned
  GATs 0.111); the distill-then-validate route matches TiMi's auditable-bot pattern.
- **The intake-wide conclusion:** six corpora — coding-agents, trading books, ML
  shelf, TS forecasting, graph ML, and now the direct stock-market ML literature —
  converge on one finding. **No corpus produced a validated daily-horizon edge, and
  the honest evaluations consistently favor simple nulls.** The verifier, not any
  model, is the product; the deliverable of the whole intake is a hardened
  verification stack (V1–V8, W1–W6, S1–S30) and a disciplined, still-gated MVP plan.

## 11. Ungating — the end-of-information decision (proposed, not recorded)

The user has declared batch 6 the final information batch. Per HANDOFF §3.2, the
end-of-information signal is the trigger to record the agreed **1–4 ungating** in
STATE.md's approved-decisions ledger. **This synthesis does not record it** — a
governance decision that lifts scope guards requires explicit, in-session user
approval, and prior-session agreement is not current consent. It is surfaced here
as the recommended next step for the user to approve or amend:

1. **Deterministic MVP on cached data** — the smallest verifiable strategy screen
   (Tier-1 families H1 momentum / H2 short-horizon reversal / H3 volatility-state
   conditioning) on a delisting-aware daily equity/ETF panel, maker≠checker,
   canonical labels, calibration-first (prove the falsification battery on the
   batch-6 known-bad specimens *before* trusting any pass).
2. **Tiingo + FRED read-only adapters** with a point-in-time cache.
3. **Bounded evolutionary strategy/factor search** disciplined by §7 (ledger charges
   every evaluated trial; DSR deflation; combination-level redundancy screening).
4. **Paper-candidate forward tracking** built on §5.1's `frozen_at` +
   strictly-post-timestamp design (S1) — the research-only, never-trade analogue of
   the live benchmarks, and the defense against the contamination gap that no
   after-the-fact detector can close.

The batch-6 verifier additions (S1–S30) are the natural first build once ungated:
the MVP's credibility rests on the harness rejecting the known-bad specimens this
corpus supplied.

## 12. Housekeeping

- **Provenance:** eight adversarial-triage agents (2026-07-22) over exclusive
  clusters of the 73 files, run as a resumable Workflow (`wf_f7d99529-662`;
  16 agents, 0 errors) after two prior Fable-model attempts died mid-run on
  spend/credit limits. Each cluster's load-bearing claims were independently
  verified inside the pipeline: **57 checked → 52 CONFIRMED, 5
  CONFIRMED-with-correction, 0 REFUTED, 0 could-not-locate.** Full digests +
  page-cited verdicts in the workflow transcript.
- **Synthesis-level check (maker≠checker on this document):** an independent
  agent re-derived the aggregate tier/verdict counts, cross-checked every
  load-bearing figure against the verified digests, and re-opened the three
  flagship PDFs (DeepFund Table 3, Stockformer Tables 5/9, Alpha Jungle Table 5)
  — all confirmed. It caught one substantive defect, now fixed: §3 had listed
  two PARTIAL-tier papers (AlphaGen, VTA) as "credible" and dropped two
  CREDIBLE-tier ones (Nexus, AI-Analyst); the §3 list and §7 label now match the
  digest tiering. Also fixed two stale "§9" cross-references. No number,
  direction, or tally was wrong, and no credible-as-tradeable-edge framing
  occurred.
- **Corrections applied by the checker** (all minor, folded into the digests): the
  Li/EIIE best traditional baseline is RMR (7.676), not ANTICOR; STOCKBENCH's +1.9%
  is in Tables 2/3, not 4; Trillion-Dollar-Words' temporal-split comparator is the
  Combined-S column (0.7113), not the speech column; "both C1D models beat WSAEs"
  holds on grand-average, not per-index; Paper 8's accuracy spread has two low
  outliers below the cited band.
- **One proposed detector rejected on verification** (§6): the
  pretrained-vs-scratch MSE-gap contamination *alarm* — low MSE is not a reliable
  contamination signature (from-scratch models also cluster low). The
  cutoff-vs-test-window *gate* (S2/S3) stands. Lesson recorded in
  `tasks/lessons.md`.
- **Duplicate handled:** TFB confirmed identical to the batch-4 paper (Qiu et al.,
  PVLDB 2024); not re-digested. Out-of-scope confirmed and dropped: People-Counting
  (retail CV), TiVy (visualization), Correlation-Is-Not-Enough (biomedical).
- **Status discipline:** everything here is `research_only` synthesis; the corpus's
  empirical claims enter the knowledge base evidence-tiered; the 10 "credible"
  papers are credible as methods/exemplars, **none as a tradeable edge**; nothing
  promotes any hypothesis or authorizes any capability. The 1–4 ungating (§11) is a
  proposal awaiting explicit user approval.
