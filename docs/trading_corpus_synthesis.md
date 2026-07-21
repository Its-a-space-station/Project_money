# Trading-Books Corpus Synthesis — hypothesis registry for Project_money

> **Research documentation (information batch 2).** Synthesized 2026-07-21 from a
> six-agent, strategically-sampled read (~1,100 of ~9,000 pages, TOC-first,
> rule/evidence chapters prioritized) of the 28-book practitioner corpus in
> `~/Documents/Github books on Trading/`. Per [CLAUDE.md](../CLAUDE.md) Part II,
> every claim here is a **hypothesis assumed false until our own cost-adjusted,
> out-of-sample validation says otherwise** — this corpus is a *hypothesis
> registry with priors*, not evidence. Companion documents:
> [agent_tooling_synthesis.md](agent_tooling_synthesis.md) (batch 1: how to
> verify) and the playbook's `reference_library.md` (the de Prado shelf: what
> rigorous validation requires). Research-only; nothing here directs an action.

## 1. The verdict in one paragraph

Twenty-eight books yield exactly **one clean modern dataset** (the
Blackstar/Wilcox-Crittenden equity trend study inside Covel: 24,000+ securities
*including delistings*, cost-modeled, +15.2% per-trade expectancy at a 2.56
win/loss ratio), **one statistical census** (Bulkowski's ~38,500 pattern
instances — usable only for its conditional frequencies and negative results,
never its hindsight perfect-trade return averages), **one honest evidence
broker** (Kirkpatrick & Dahlquist, who aggregate the academic record: momentum
validated, channel systems historically supported, patterns marginal,
candlesticks weak and decaying, volume folk-rules unreliable), **one
methodology-transparent strategy catalog** (Chan, who self-flags every backtest
bias), and **one large-sample system developer** (Fitschen, whose asset-class ×
timeframe tendency map and genuine falsifications are cheap to re-verify).
Everything else — roughly 20 books — is folklore ranging from
mechanism-rich-but-unquantified (the price-action school) to precision-without-
validation (pivots, harmonics) to null-by-construction (financial astrology).
The corpus's real value is threefold: a **bank of edge-existence mechanisms**
(who is on the other side), a **catalog of exactly-specified rules** ready for
the hypothesis ledger, and a set of **documented nulls and convergent
warnings** that seed the falsification battery.

## 2. Source evidence tiers

Rubric: **T1** systematic backtest with disclosed methodology · **T2** partial
quantitative evidence or honest evidence review · **T3** structured rules with
anecdotal/unaudited validation · **T4** chart anecdote or no plausible
mechanism.

| Tier | Sources |
|---|---|
| T1 | Chan *Algorithmic Trading*; Fitschen *Building Reliable Trading Systems* (borderline: full-sample validation, no held-out) |
| T2 | Kirkpatrick & Dahlquist (evidence review); Bulkowski *Encyclopedia* (census, T2–3); Blackstar study (inside Covel App. A); Grimes *Art & Science* (tests against randomness, little printed methodology); Saettele *Sentiment* (reproducible constructions, curated validation); Soros *Alchemy* (theory + one audited-style track record, T2–3); Schwager *Wizards* (T2 for cross-replicated process doctrine, T3 for returns) |
| T3 | Abraham (complete spec, anecdotal validation); Brooks (mechanism-rich, unaudited probabilities); Volman (coherent, unquantified); Carr (screens fully specified, newsletter anecdotes); Smith (orthodox trend rules + one borrowed backtest table) |
| T4 | Murphy (assertion compendium); Nison ×2 (candid about subjectivity; deterministic chart grammars are the exception); Farley ×2; Landry (rules T1-grade codeable, evidence T4); Miner; DraKoln; Covel narrative chapters; Coulling; Person ×2; Carney ×2; Lee/Tryde (astrology: lowest) |

## 3. The mechanism bank — why should any edge exist?

Every hypothesis entering the ledger must name its mechanism (CLAUDE.md §12).
The corpus converges, across independent authors and eras, on nine:

1. **Counterparty exhaustion / two-sided auction** — price moves while one
   side's liquidity fails; impulses end when the aggressor runs out of
   counterparties (Grimes's motive/resistive forces, Brooks's "no one left to
   short," Volman's double pressure, Coulling's absorption).
2. **Stop-clustering and trapped traders** — resting stops pool behind salient
   references; probes that spring them reverse, breaks that trap a committed
   side run (all four price-action authors independently; Landry's shakeout
   re-entries; Livermore's line-of-least-resistance; Chan cites Osler's
   stop-hunting microstructure).
3. **Herding + slow information diffusion** — serial correlation from unequal
   information and crowd behavior (AHL via Covel; K&D's underreaction
   literature; the academic momentum canon).
4. **Reflexivity** — where price changes alter fundamentals (issuance, credit,
   collateral, credibility), trends self-reinforce beyond equilibrium and snap
   at bias-reality divergence; corrections becoming scarcer marks late stage
   (Soros — the corpus's only full theory of edge existence *and* decay).
5. **Forced / mechanical flows** — leveraged-ETF close rebalancing, fund-flow
   pressure, index membership changes, portfolio-insurance-style cascades
   (Chan's measured examples; Schwager's popularity-destroys-approaches).
6. **Hedging pressure / risk transfer** — futures roll states persist because
   hedgers pay for insurance; carry is compensation (Chan; Murphy's COT
   commercials logic).
7. **Behavioral hope/fear inversion** — the public cuts winners and rides
   losers, funding trend persistence and panic reversion (Livermore's base
   rates; Fitschen's emotion-asset claim; wizards' loss-limit universality as
   the countermeasure).
8. **Focal-point coordination** — widely-watched deterministic levels (pivots,
   round numbers, MA lines) may self-fulfill via order clustering (Person's
   floor lineage, Volman, Murphy; round-number clustering has academic
   contact) — genuinely testable against placebo levels.
9. **Institutional order-splitting** — large orders worked over days produce
   impulse-pause rhythm and absorption signatures (Grimes, Coulling/Wyckoff);
   the observable residue is testable, the intent narrative is not.

## 4. The consolidated hypothesis catalog

Deduplicated across all six clusters. **Conv** = independent in-corpus
attestations; **Lit** = external literature contact (via K&D, Chan, or the
reference-library shelf). Priors are qualitative and deliberately conservative;
formal multiplicity accounting happens in the ledger at test time. Families
enter the ledger as `proposed`; nothing here carries a promoted label.

### Tier 1 — external validation + mechanism + fully codeable (MVP seed set)

| ID | Family | Core hypothesis | Conv | Lit |
|---|---|---|---|---|
| H1 | **Momentum / trend continuation** (12-1 cross-sectional; Donchian/channel time-series; ATH continuation with wide trailing exits) | 3–12-month relative and absolute strength predicts continuation; long-horizon breakouts carry right-skewed expectancy | 8+ (canon, Blackstar, Covel, Abraham, Smith, Chan, Livermore, Soros) | Strong: JT93/01, Moskowitz-Ooi-Pedersen, Lukac-Brorsen, Fama-French |
| H2 | **Short-horizon equity mean reversion** (cross-sectional 1-day; n-day-low oversold bounce; conditional overnight-panic reversion) | Daily-bar equity weakness precedes above-average forward returns; moderate extremes beat falling knives; trend + volatility filters condition it | 3 independent quant sources (Chan, Fitschen ×2 families) | Khandani-Lo; short-term-reversal factor |
| H3 | **Volatility-state conditioning** (VIX bands, realized-vol filters, vol-inverse sizing) | The same signal's expectancy is regime-dependent with *opposite* signs across strategy types (reversal doubles / gap momentum dies at high VIX) | 4 (Chan's sign-asymmetry result, Fitschen's vol gate, Abraham's quiet-market convexity, Soros's vol-rise-at-exhaustion) | Vol-managed portfolio literature |
| H4 | **Carry / roll-state persistence** (futures curve slope as signal; contango-state switching) | Roll-state sign persists for months and dominates long-hold returns in futures-linked instruments | 1 deep (Chan) + Murphy's COT hedging logic | Hedging-pressure/carry literature |
| H5 | **Forced-flow effects** (leveraged-ETF late-day rebalance continuation; flow-pressure reversal; index changes) | Mechanical, non-informational flows create predictable pressure with dose-response in product AUM | 2 (Chan measured; Schwager structural) | Coval-Stafford; Cheng-Madhavan |
| H6 | **Volatility contraction → expansion** (NR7/NR4, coils, base contraction, buildup-at-level) | Range contraction predicts expansion; contraction *at a boundary* predicts direction quality | 5 (Farley, Carr, Grimes, Volman, canon; Crabel lineage) | Crabel's published work |

### Tier 2 — convergent folklore with plausible mechanism (search-loop population)

| ID | Family | Core hypothesis | Conv | Notes |
|---|---|---|---|---|
| H7 | **Trend-gated pullback continuation** | In a mechanically-defined trend regime, 3–7-bar / 25–75% retracements resolve with the trend; early pullbacks beat late; confirmation-stop entries | 5 (Landry, Carr, Farley, Miner, Grimes) | The corpus's single most convergent setup skeleton; test each layer as ablation |
| H8 | **Failure-test / stop-run fade** | Probes beyond salient extremes that close back inside within 1–3 bars revert; sign conditioned on trend context and pre-break buildup | 5 (Grimes spring/2B, Volman trio, Brooks, Landry TKO, Livermore) + Bulkowski's 64% pre-confirmation failure base rate | Deterministic; mechanism #2 |
| H9 | **Breakout-quality scoring** | P(follow-through) is a function of buildup tightness, higher-lows-into-level, breakout-bar expansion, closes-reversed count, touch count, extension caps | 4 (Grimes, Brooks, Volman, Farley/Carr specs) | Logistic-model design; K&D system evidence adjacent |
| H10 | **Post-signal throwback window** | Breakouts retrace to the broken level ~50–65% of the time within ~2 weeks; profit accrual after popular signals is delayed 7–20 days → delayed entries beat chasing | **2 independent quantitative sources converge** (Bulkowski census; Fitschen's adverse-drift study) | One of the corpus's best cross-cluster surprises |
| H11 | **Exhaustion / climax reversion** | After extended trends: consecutive outsized bars, channel-escape bars, 3–5× volume spikes → multi-leg correction; climax extremes persist as levels | 4 (Grimes, Brooks's parameterized claim, Farley, Coulling) | Brooks's 30-bar/2-leg/10-bar prediction is directly testable |
| H12 | **Positioning & sentiment two-regime model** | Follow speculative positioning mid-range; reversal risk only at triple-aligned extremes (COT percentile + spec ratio + commercial opposite); media saturation and retail-flow flips as saturation markers | 3 (Saettele's framework, Murphy's COT chapter, wizards' popularity lesson) | CFTC data is free; 3-day staleness must be modeled |
| H13 | **Retracement-depth structure** | Correction terminations cluster at 50–61.8%; ≥75–78.6% penetration flips the regime (continuation → reversal odds) | 3 precise statements (Miner, Brooks's 75% cliff, Farley) | Pure distribution claim — falsifiable without any strategy |
| H14 | **Swing-structure change of character** | First countertrend swing exceeding the prior with-trend swing (price or time) warns of trend change; pullback-failure hazard rises with leg count | 3 (Grimes, Brooks, Farley Toolkit) | Needs pivot grammar (kagi/zigzag — Nison supplies deterministic constructions) |
| H15 | **Effort-vs-result volume anomalies** | Narrow-spread/high-volume absorption at extremes and low-volume tests of base lows carry information beyond price | Coulling's matrix + Wyckoff lineage **vs** Grimes's volume-null and K&D's folk-rule skepticism | A designed adversarial head-to-head; signed-volume literature (Blume-Easley-O'Hara) referees |
| H16 | **Range dynamics & level decay** | Range interiors ≈ random; resolution defaults to prior trend; a level's break probability rises with touch count 3+ | 3 (Grimes, Brooks, Volman squeeze) | Anti-classical (folk lore says more touches = stronger) — good discriminating test |
| H17 | **Gap dynamics** | Area gaps fill ~90% within a week; large breakaway gaps persist months; first test of an in-trend gap holds on low volume | Bulkowski distributions + Farley + Person's "Oops" | Avoid ex-post gap-type labels; condition on size/trend position only |
| H18 | **Event drift conditional on trend/sentiment state** | News lands "in harmony with" the trend; announcement gaps >0.5σ continue intraday; the historical multi-day drift has compressed (decay) | 3 (Livermore, Chan's PEAD + decay observation, Saettele's release-direction null) | Includes its own alpha-decay model |
| H19 | **Reflexive late-cycle markers** | Net issuance, M&A intensity, credit-growth deceleration flag self-referential boom stages with poor long-horizon forward returns | Soros channels + Schwager's index-concentration | Issuance anomaly literature; slow data, strong theory |
| H20 | **Strategy-level drawdown mean reversion** | Forward returns after −10/−20/−30% strategy drawdowns exceed unconditional (JWH 25/28, 10/10, 3/3; Dunn) | 2 (Covel's tables, Abraham's allocation practice) | Small-n, fund-selected; test on our own simulated equity curves instead |

### Tier 3 — low-prior falsification batteries (documented-null candidates)

| ID | Family | Prior | Value |
|---|---|---|---|
| H21 | **Focal-level coordination** (pivot formulas vs distance-matched placebo levels; round numbers) | ~10–25% | The one genuinely testable claim in the pivot genre; round-number clustering has academic support |
| H22 | **Harmonic ratio precision** (exact Fibonacci boxes vs generic-pullback control) | ~5% | Converts a popular retail doctrine into a citable null (or a surprise); tolerances pre-registered |
| H23 | **Frozen-threshold candlestick set** (hammer/engulfing/dark-cloud + confirmation close, small pre-registered set) | ~10–15% | Caginalp-Laurent positive but decaying; context-gated only |
| H24 | **Calendar effects** (best-six-months + MACD timing; lunar-phase replication) | ~10–15% statistical, ~2% net | Cheap; lunar effect has peer-reviewed contact but weak/unstable |
| H25 | **Astrology-derived timing** (eclipse/aspect dates) | ~2% | Null-by-construction; run once as a falsification-harness calibration exercise |

### Documented nulls the corpus itself supplies (seed the ledger as prior rejections)

- **Momentum/price divergence signals are anti-predictive** (Fitschen, thousands
  of trades; fading them was profitable) — despite being ubiquitous folklore.
- **Macro-release direction has no stable FX edge** (Saettele's rolling-sign
  instability; Chan's FOMC/CPI null — two independent sources).
- **Measure-rule price targets usually miss** (Bulkowski: 54% of bull H&S never
  reach their projected decline).
- **Anticipating pattern confirmation is negative-edge** (64% of twin-bottom
  lookalikes fail before confirming).
- **Heavy breakout volume is not required** for pattern success (Bulkowski),
  and folk volume-confirmation rules are unreliable (K&D, Grimes) — only
  *signed* volume carries documented information.
- **High-win-rate/negative-skew profiles blow up** (Niederhoffer three times;
  Abraham/Covel arithmetic) — the corpus's standing warning against optimizing
  win rate, converging with our §11 priority order (CAGR/robustness, never
  excitement).

## 5. Process doctrine the corpus adds (research-only translation)

The practitioner consensus maps cleanly onto machinery we already built:

1. **Predefined invalidation on every position** (the single universal wizard
   habit; Livermore; Abraham's hard stops) → every belief card carries explicit
   failure conditions and monitoring criteria *before* evaluation
   (CLAUDE.md §16); the research analog of the loss limit is the pre-registered
   kill criterion.
2. **The edge is enforced, not found** — asymmetric exits, sizing to survive,
   taking every signal — converging with our doctrine that verification
   discipline, not signal cleverness, is the product.
3. **Regime attribution before trust** (Schwager lesson 56: past performance is
   conditional on its enabling regime) → the leakage auditor's formation-date
   discipline plus regime breakdowns in the cascade.
4. **Edge-decay monitoring** (crowding, adaptation, regime change; Soros's
   vol-rise signal; Chan's PEAD-compression observation) → monitoring fields in
   belief cards; scheduled recalibration; the corpus predicts published edges
   attenuate — including everything in this catalog.
5. **Fitschen's validation critiques** — IID trade-resampling Monte Carlo is
   invalid (destroys range anti-persistence, autocorr −0.43 to −0.48, and
   cross-sectional trade clustering); 30-trade samples prove nothing; metric
   choice is part of the search space → adopt block bootstraps,
   clustered-by-day inference, and metric pre-registration in the falsification
   harness. His BRAC (parameter-stability under truncation) joins the cascade
   as a *complement* to held-out validation, never a substitute.

## 6. Integration with prior corpora

- **Multiplicity is the binding constraint everywhere.** Bulkowski's hundreds
  of uncorrected cells, Chan's parameter grids, Miner's tuned-by-eye lookbacks,
  and the harmonic tolerance bands are all the "selection-on-noise" failure the
  batch-1 synthesis centers; every catalog test runs through the hypothesis
  ledger's trial registry and deflated-Sharpe machinery.
- **Survivorship decides Tier-1 tests.** The corpus's one clean dataset
  (Blackstar) is clean *because* it included delistings; Chan flags his S&P
  universes as biased. Data-acquisition implication recorded: the equity panel
  behind any H1/H2 test must be delisting-aware and point-in-time (relevant to
  the gated Tiingo adapter's scope).
- **New provider candidate:** CFTC COT weekly data (free, public) for H12 —
  noted for the provider roadmap; remains gated like all adapters.
- **The books' in-sample tuning habits** (Miner's oscillator-by-eye; Carr's
  ADX-collapse thresholds) are the checker-leak the generator↔gate firewall
  exists for: parameters from this catalog enter specs as *pre-registered
  ranges*, never as tuned constants with authority.
- **Reflexivity (Soros) upgrades the "why does the edge decay" question** from
  folklore to a mechanism with named observables (issuance, credit growth,
  correction scarcity) — these become monitoring-field candidates on momentum-
  family belief cards.

## 7. Implications for the MVP and the ungating plan

The catalog **sharpens, and does not reorder,** the agreed 1–4 ungating plan:

1. The **MVP slice** has an obvious seed: Tier-1 families (H1, H2, H3) on daily
   equity/ETF data — the strongest mechanism + literature + convergence, and
   they exercise every part of the verification backbone (trend gates,
   conditional expectancies, regime splits).
2. The **search loop** gets its initial population (Tier 2) and its ablation
   design doctrine: convergent-skeleton first, layer-by-layer marginal-value
   tests (oscillator confirmation, volume conditions, entry mechanics) instead
   of whole-system tuning.
3. The **falsification harness** gets calibration material (Tier 3 + the
   documented nulls): known-low-prior claims to prove the battery rejects, and
   the corpus's own falsifications as regression cases.
4. **Paper tracking** inherits the corpus's decay doctrine: every promoted
   candidate ships with crowding/regime monitoring criteria from §5.4.

No change to gate order or scope is warranted by this batch.

## 8. Housekeeping

- Coverage gaps (TOC-verified, not extracted; transcribe before writing any
  implementation spec that needs them): Landry's Bow Ties/volatility screens;
  Carr's five bearish mirrors + market-direction chapter; Farley's Finger
  Finder/First Pullback and Toolkit gap plays; Miner's exit chapter; Carney's
  Alternate Bat elements + RSI-BAMM state machine; Smith's inside-day/Slingshot
  chapters + exact Conqueror stop multiples; DraKoln's seasonal spreads.
- Reading-agent honesty flags carried forward: Brooks's probabilities are
  experiential assertions; Covel's fund tables are survivorship-saturated;
  Bulkowski's regime split confounds one specific crash; all Person "backtest"
  claims are unsubstantiated in-text.
- Two agents (trend-following/classics; low-evidence tier) were interrupted by
  API errors mid-read and resumed from transcript; their final deliverables are
  complete.
