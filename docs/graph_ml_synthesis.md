# Graph-ML Corpus Synthesis — batch 5 fresh read

> **Batch 5 of the information intake** (2026-07-21). Corpus: 25 PDFs in
> `~/Documents/PWC_graph_ML/` — graph neural networks, graph transformers,
> knowledge graphs, GNN benchmarking/robustness, interpretability/symbolic
> extraction, GNNs-for-time-series, physics/equivariant simulation, and the
> PyG/PyTorch-Frame tooling stack. Confirmed new territory (zero overlap with
> the playbook or prior batches) → **fresh-read pattern** (batch-1/2 style),
> five agents over exclusive clusters, page-cited digests, followed by an
> independent checker pass on this document's load-bearing figures.
> Research-only throughout; nothing here authorizes ML, graph features,
> providers, or any action. **Zero papers in this corpus contain a finance
> experiment** — every finance-transfer statement below is out-of-domain
> extrapolation, `validation_pending` at best.

## 1. Verdict

**This corpus refines rather than expands: it produces no capability case for
graph ML on our panels today, and instead sharpens our nulls, extends the
verifier queue, tightens do-not-build boundaries, and contributes one
genuinely new pipeline pattern.** The batch-4 MTGNN do-not-build verdict was
explicitly hunted for overturning evidence and **survived — confirmed by the
GNN4TS survey's own catalog, reinforced from two new directions, and
corrected on one boundary** (§3). The single most valuable import is
Cranmer's **distill-then-validate** result (§5.2): a symbolic formula
extracted from a trained GNN was worse in-sample and substantially better
out-of-distribution than its own teacher network — our central doctrine
(in-sample fit anti-correlates with robustness) demonstrated inside one
peer-reviewed experiment.

The corpus also delivers third-domain corroboration of baselines-as-nulls:
the KGC field re-learned that headline gains over under-tuned baselines
evaporate (R-GCN's +29.8% vs later tuned DistMult/ComplEx); standardized
re-evaluation erased most published GNN pooling gains (PyG's own paper); and
the tabular-DL framework paper concedes in its own benchmark that **LightGBM
"is still dominating" deep tabular models** on conventional data — from the
authors whose commercial premise is deep tabular learning. Three fields, one
lesson, same as batches 2–4.

## 2. Cross-cluster convergences (the corpus's own evidence)

1. **Given structure beats learned or discarded structure.** Full-graph
   attention destroys performance vs attention masked to the given graph
   (Dwivedi–Bresson: PATTERN 84.81→54.94, CLUSTER 73.17→27.12); GPS's
   ablations show the structure-respecting MPNN is the indispensable module
   while global attention is sometimes worthless (ZINC); and every
   learned-graph success GNN4TS tabulates lives on physically-structured
   domains — where the learned graph is essentially recovering a stable
   exogenous structure that could have been supplied as a prior.
2. **Under-tuned baselines inflate headlines — third independent domain.**
   R-GCN's +29.8% over DistMult (0.248 vs 0.191 FB15k-237 MRR) was later
   reversed by properly tuned decoders (≈0.30+); re-tuned plain MPNNs closed
   most of the graph-transformer LRGB gap; PyG's standardized re-evaluation
   found "not all results are aligned with their official reported values"
   and most pooling gains vanish. Same failure the forecasting corpus
   (batch 4) documented via TFB.
3. **Compression must be trained in, not read off afterwards.** Cranmer's
   grid: symbolic recovery 0/8 from unconstrained networks, 8/8 with a
   bottleneck constraint (and 6/8 with L1, which fails both Charge systems —
   the regularizer is a results-determining knob). GNNExplainer needs
   explicit sparsity regularizers; DepGraph's group-sparse training makes
   coupled parameters consistently unimportant before removal. Post-hoc
   simplicity extraction from an unconstrained model recovered nothing.
4. **Evaluation pathologies recur, documented by the field itself:**
   FB15k/WN18 inverse-pair leakage where the trivial LinkFeat baseline
   (filtered MRR 0.779 on FB15k, 0.938 on WN18) beat every learned model on
   FB15k (on WN18 ComplEx edges it, 0.941) and collapsed to 0.063 on the
   de-leaked FB15k-237; OGB-LSC's self-reported wrong-grouping-key split bug
   (CID vs scaffold — the paper reports conclusions held across both splits,
   so cite it as a precedent for the check, not as a changed result);
   WikiKG90M's too-easy negatives (frequency-sort reaching MRR 0.75,
   rivaling a trained baseline; benchmark saturated and was replaced);
   VGAE's balanced-AUC protocol overstating deployment performance; the CSL
   result that message-passing GNNs score exactly chance (10.0%) without
   positional encodings while GCN with Laplacian PE reaches 100% (the other
   GNNs 99+) — the input representation, not capacity, decides learnability.
5. **Parsimony votes from physics:** MeshGraphNets found shortest history
   best — extra history *overfits*, contradicting its own predecessor's
   practice; E2Former honestly reports its win is asymptotic memory, not
   speed. High-SNR domains rediscovering MDL.

## 3. Disposition of the batch-4 MTGNN verdict

- **Confirmed.** GNN4TS Table 2 classifies MTGNN exactly as batch 4 read it:
  input graph **not required**, learned static adjacency, **no** heuristics.
  No paper in this corpus tests a learned graph on financial data; finance
  appears in the survey only as passing mentions (an "other applications"
  clause and intro domain lists) with zero methodology, datasets, or
  evaluation.
- **Reinforced from two new directions.** (a) VGAE-style link discovery
  re-enters the same minefield generatively: scoring all pairs of an N=500
  universe is ~125k implicit hypotheses, the inner-product decoder can
  express only homophily (it rediscovers the sector partition), and the
  1:1-balanced evaluation hides base-rate reality. (b) The refined survey
  reading: learned graphs are evidenced only where stable exogenous
  structure exists — precisely the case where the structure can be supplied
  as an auditable prior instead.
- **One boundary correction to how batch 4 is quoted.** The multiplicity
  argument ("freely-learned N×N = O(N²) minefield") does **not** condemn
  attention *masked to a prior graph*, which is O(d) parameters (GAT: one
  shared W and a). Corrected doctrinal statement: **masked attention escapes
  the O(N²) objection but remains unjustified at our SNR until fixed-weight
  nulls are exhausted** — see the ablation ladder (§5.1). Batch 4's verdict
  stands; its rationale must not be over-applied to the constrained case it
  left open.

## 4. Verifier and policy additions

### 4.1 New verifier build items (W-queue; joins batch-4 V1–V8 in sequencing)

| # | Item | Source | Sketch |
| --- | --- | --- | --- |
| W1 | **Known-positive control (discriminative-power precheck)** | Benchmarking GNNs' graph-agnostic-MLP check | The falsification harness guards false positives (known-zero controls); nothing guards false negatives. Plant a known-strong signal; if the evaluation cannot separate it from a known-weak one, the eval lacks power and its passes/fails mean little. Mirror image of the existing controls. |
| W2 | **Split-key provenance + split-scheme invariance** | OGB-LSC's self-reported CID-vs-scaffold bug (results held across splits — a precedent for the check, not a changed conclusion) | Assert the partition key is the intended one; assert no group straddles train/test; re-run under one alternative reasonable split and flag conclusions that are not split-invariant. Purge/embargo covers temporal leakage, not wrong-grouping-key errors. |
| W3 | **Cheap-heuristic null battery** | WikiKG90M frequency-sort (MRR 0.75) | Trivial heuristics can masquerade as skill. Add popularity/size/recency/last-value/sort-by-obvious-covariate nulls as a distinct class beside the known-zero controls; candidates must beat them on the same budget (extends V2). |
| W4 | **Full-search-space trial accounting for DSR** | AutoML-on-graphs survey (one-shot super-networks) | A differentiable/one-shot search implicitly evaluates its whole space (thousands+); feeding DSR only reported-winner counts is anti-conservative — the batch-3 defect class again. Ledger rule: register the search space cardinality as the trial count before any search runs. |
| W5 | **Stratified noise-injection robustness diagnostic** | DP-GNN reframe + its rare-class finding | Plot performance vs calibrated injected noise; real edges degrade gracefully, overfit edges collapse. MUST be stratified by regime — DP-GNN shows noise disproportionately destroys under-represented strata, so an unstratified probe hides rare-regime fragility (would silently contradict V5). Diagnostic, not a gate, until checker-validated. |
| W6 | **Capacity-matched comparison rule** | Benchmarking GNNs' fixed parameter budgets | Head-to-head strategy comparisons match on degrees of freedom, not just search compute — extends V2 and the MDL gate. Mostly a spec clause. |

### 4.2 Policy clauses (documentation-only, no gate needed)

- **Interpretability-as-falsification-only** (GNNExplainer + faithfulness
  critiques): model-attribution audits are admissible solely as *negative*
  evidence — leakage/artifact detection, demotion. Post-hoc explanations are
  never admissible as economic rationale; rationale must predate the fit.
  Attention weights specifically are disqualified as an audit surface
  (static-attention defect, seed instability; the authors themselves decline
  to interpret them).
- **Correlated-LLM-blind-spot rule** (knowledge homophily): LLM knowledge
  failures are spatially correlated (homophily ≈0.8 vs degree-matched null,
  p<0.01), so two LLM readers do not constitute independent checks for
  tail/obscure entities (microcaps, niche series, recent events). Route
  tail-entity claims to source-grounded or human verification; allocate
  checking budget inversely to expected LLM familiarity; degrade extraction
  confidence with entity obscurity.
- **"No estimated numerics" made empirical** (RLM-for-code): even a frontier
  LLM with ~50-shot in-context examples "remains consistently below" a
  300M-parameter trained regressor at predicting numbers from code — and
  that regressor itself tops out at screen-grade reliability (54.4%
  within-problem discriminability). Fleet LLMs never eyeball-estimate
  metrics, costs, or outcomes in lieu of executing code; learned proxies may
  prioritize, never promote (Goodhart, per batch 4).
- **Leakage-precedent catalog additions**: inverse/near-duplicate-pair rule
  (run a trivial memorization baseline first — if LinkFeat-style wins, the
  benchmark is the finding); correlated-sibling target-leakage rule (the
  MUTAG catch: removing the target column is insufficient when siblings
  encode it); base-rate re-basing rule (balanced-sampling metrics must be
  restated at deployment base rates); embedding-vintage rule (a modern
  embedder applied to historical text is a look-ahead channel — extends V3);
  normalization-stats scoping rule (PyTorch Frame computes imputation/
  normalization statistics over the full materialized table — any tabular
  pipeline must recompute per training window).
- **Graph-construction leakage checklist** (GNN4TS taxonomy): any future
  proposal introducing a graph is classified {prior-defined | similarity |
  learned}; prior-defined → auditable + **graph-vintage discipline** (edges
  as-known-at-t; supply-chain/ownership links are revealed with lag);
  similarity (correlation/DTW) → point-in-time windows + multiplicity
  budget; learned → the §3 verdict applies.
- **Iterated-vs-one-step verifier question** (mesh cluster): any multi-step
  forecaster states whether it was trained for iterated use; require an
  error-compounding check.
- **Non-additive-score warning** (DepGraph): heterogeneous importance/
  quality scores are "non-additive and thus meaningless" when naively
  summed — any composite ranking across pipeline stages requires an explicit
  comparability argument.
- **Fleet prompting** (GraphGPT, measured): serialize relation structures
  compactly (750 vs 4,649 tokens for the same subgraph); verify structure
  actually altered an LLM's conclusion rather than assuming it did.

## 5. Gated-future pre-specifications (require ML authorization; recorded now)

### 5.1 The graph-null ladder and the typed-linear-propagation null

If a relational hypothesis is ever authorized, the ablation ladder is
pre-registered from this corpus's own controls: **rung 0** no graph →
**rung 1** uniform propagation on the prior graph (the Const-GAT move ≈
sector-mean factor) → **rung 2** typed propagation → **rung 3** learned
scalar weights → **rung 4+** anything neural. Each rung must beat the
previous under DSR over the declared grid, or the ladder stops.

The rung-2 null is fully specified: a 1-layer linear scalar R-GCN is
algebraically a **per-relation-type neighbor-mean WLS regression** with
|R|+1 ≤ ~7 parameters (vs ~250k for MTGNN-class on N=500 — a ~10⁴×
description-length reduction), using R-GCN's canonical+inverse relation
doubling for directional relations (supplier→customer ≠ customer→supplier).
Pre-declared failure modes: mega-cap hub pathology (R-GCN's own
normalization failure at high-degree nodes); **sector-mean collapse** —
over-smoothing read financially: iterated propagation converges to the
sector factor and destroys exactly the idiosyncratic component that contains
alpha, so cap depth at 1–2, keep the self-loop term, and gate on incremental
R² over the sector factor, never gross fit; and regime dependence. Note the
value of graph context is plausibly *anti-correlated* with residual alpha
(dense neighborhoods = most-arbitraged names).

### 5.2 Distill-then-validate-the-symbolic-form (new pipeline pattern — earns a place in the future hypothesis-pipeline spec)

Pattern: a flexible learned model that survives screening is **distilled to
a closed form (symbolic regression on its separable internals), and only the
closed form enters the validation cascade, walk-forward, and reporting**;
the teacher's performance is inadmissible as evidence for the formula.
Supporting evidence (independently checker-confirmed after drafting — see
§8): Cranmer's distilled expression was
worse in-sample (0.0811 vs 0.0634 MAE) and better out-of-distribution
(0.0892 vs 0.142) than its own teacher GN; the extracted cosmology formula
beat the domain-expert baseline (0.0882 vs 0.121). Pre-registered gates:
(a) operator set, complexity measure, and knee-point selection rule fixed
ex-ante (Cranmer's −Δlog(MAE)/Δc maps onto our per-knob bits hurdle);
(b) the SR search size is charged to the DSR/multiplicity budget (SR is an
industrial-scale multiplicity engine); (c) the extracted form must beat the
baselines-as-nulls on data the network never touched; (d) extraction
*failure* is logged as evidence against the learned model (verification
debt), never silently dropped; (e) the sparsity/bottleneck strategy is
pre-registered (it is a results-determining knob — L1 failed both Charge
systems). Scope honesty: demonstrated where a true compact law exists in
near-noiseless simulation; GP-based SR degrades sharply with noise; a failed
extraction on market data may mean "no compact edge exists," which is itself
informative. **Doctrinal refinement made explicit:** direct SR on raw data
failed in Cranmer's own control — MDL simplicity governs *what may enter
validation and be believed*, not *how the search must proceed*; flexible
intermediate models are permitted as scaffolding.

### 5.3 Tabular-DL evaluation spec (if ever authorized) and nearer-term utilities

- **PyTorch Frame vs GBDT nulls**: preconditions — data layer ungated, a
  registered hypothesis specifically requiring multi-modal columns, explicit
  torch-dependency authorization (CPU-only, pinned, deterministic-mode,
  5-seed spread; PyG's own paper documents GPU scatter non-determinism
  breaking seed reproducibility). Null ladder: N0 ridge/logistic on
  engineered features; N1 LightGBM/XGBoost at **equal** tuning budget
  (repairing Frame's own 3-trials-vs-manual asymmetry); N2 LightGBM on
  [engineered ⊕ flattened embedding features] — the construction that nearly
  tied their best deep model. N2 isolates architecture value from embedding
  value. Per-window materialization stats; no entity-ID features;
  vintage-checked embedders only. Decision rule: beat N1 *and* N2 OOS with
  DSR-adjusted significance by a pre-registered operational-cost premium;
  ties → GBDT retained.
- **Assignment-with-dustbin entity resolution** (from SuperGlue's matching
  layer, deterministically reduced): exact-key + fuzzy similarity score
  matrix → append explicit no-match dustbin → Hungarian assignment
  (`scipy.optimize.linear_sum_assignment`) → unmatched entities become
  tracked verification debt, never silent forced matches. CPU, deterministic,
  zero new dependencies; enforces mutual exclusivity greedy matching lacks.
  Buildable when the data layer ungates (vendor cross-mapping for the
  delisting-aware panel). Highest-value tooling transfer in the corpus.
- **Semantic-type schema discipline** (Frame's taxonomy, not its library):
  adopt the column-type vocabulary into panel schema docs, extended with
  per-column missing-value policy, normalization-stats provenance, and
  vintage/embedder-date fields. Documentation-only; can be drafted now.
- **Centrality covariates** (degree/hubness of a prior graph) as named,
  pre-declared conditioning variables in linear analyses — feature
  engineering, no graph network required.
- **Noise-injection/scheduled-sampling regularizer** for iterated
  forecasters (mesh cluster's rollout-stability trick) — gated behind
  "beats the same model trained one-step, OOS"; low-SNR caveat: injected
  noise rivals signal in markets.

## 6. Do-not-build ledger (with reasons)

1. **Learned N×N stock graphs** (embedding/attention/probabilistic
   adjacency) — batch-4 verdict re-affirmed; survey adds no finance evidence.
2. **VGAE/GAE latent link discovery over stock pairs** — O(N²) multiplicity
   family; decoder expresses only homophily (rediscovers the sector
   partition); MDL-dominated by the partition itself.
3. **Learned attention (GAT/GATv2) as alpha model or audit surface** —
   fixed-weight nulls must be exhausted first; static-attention defect and
   seed instability disqualify the audit use.
4. **Graph-transformer stacks (GT/GPS) for equity panels** — their
   motivating problems (long-range dependency, anonymous nodes, 1-WL
   expressivity) are absent on small-diameter, feature-rich, identity-labeled
   stock graphs; flagship long-range evidence later deflated by re-tuned
   baselines.
5. **Full KG-embedding stack over a financial KG** — tiny known relation
   vocabulary; KGC solves missing-fact recovery at scale, not low-SNR signal
   extraction; imports a benchmark culture with documented leakage
   pathologies. Index the survey's machinery; build nothing.
6. **GraphGPT-style graph instruction tuning** — multi-A100 infrastructure
   for benchmark-bound gains (like-for-like +3–7 points, not the headline
   2–10×, which is against structurally handicapped baselines).
7. **SuperGlue the network / any learned matcher** — no supervision source;
   the deterministic assignment utility captures the transferable idea;
   pretrained weights likely non-commercial-licensed.
8. **Deep tabular models on conventional numerical/categorical panels** —
   contraindicated by the framework authors' own benchmark.
9. **Mesh/equivariant machinery** (MeshGraphNets, Transformer-mesh,
   E2Former, spherical SE(3) stack) — no financial object has a mesh or
   SO(3) symmetry; keep only the two disciplined analogies (§4.2 iterated
   check, §5.3 noise injection) and the constraint-only-where-invariance-
   is-real template, which is our economic-prior gate stated in physics
   language.
10. **DP machinery** — no privacy requirement over non-personal market data;
    keep only the stratified-noise-probe reframe (W5).
11. **NAS/strategy-search engines** — until eval is locked and W4 trial
    accounting exists, search is a false-discovery engine; the AutoML survey
    itself concedes its field runs on inadequate benchmarks.
12. **Structural pruning tooling (DepGraph)** — solves deployment
    efficiency we don't have; keep the dependency-propagation hygiene
    pattern (deprecating a data field auto-flags every derived feature) and
    the non-additive-score warning.
13. **RLM-style learned proxies as verifiers or gates** — unverifiable +
    gameable; screen-only if execution ever becomes the bottleneck, with
    admission-gate calibration and a ban on the score appearing in promotion
    decisions.
14. **Any GPU-dependent training path** — until determinism is proven
    mitigated (PyG's own non-determinism admission); CPU-only with
    deterministic-mode flags otherwise.

## 7. Crosswalk and ungating impact

- **Batch 1 (agent tooling):** the correlated-blind-spot rule and
  no-estimated-numerics evidence directly harden fleet/verifier doctrine;
  RLM-as-oracle is the verifier-is-the-product anti-pattern named.
- **Batch 2 (trading corpus):** unaffected; H1–H3 remain the MVP seeds. The
  entity-resolution utility serves the delisting-aware panel requirement.
- **Batch 3 (ML shelf):** W4 is the same anti-conservative-DSR defect class
  the batch-3 correction fixed, now at the search layer; W-items join the
  batch-3 follow-on list and batch-4 V-queue in one sequencing pool.
- **Batch 4 (TS forecasting):** MTGNN verdict confirmed + boundary-corrected
  (§3); the GBDT-null result extends the linear-null evidence to tabular
  architectures; two non-transferable optimisms pre-rebutted for the record
  (random-edges-help and physics scaling laws — both high-SNR artifacts).
- **Ungating impact: sharpens, does not reorder.** Nothing here changes the
  agreed (unrecorded) 1–4 plan; the corpus strengthens the case that ML
  stays deferred (a third domain's worth of nulls-win evidence) while
  pre-specifying exactly what any future ML/graph work must beat. Recording
  still waits on the user's end-of-information signal.

## 8. Housekeeping

- **Provenance**: five fresh-read agents (2026-07-21), exclusive clusters
  over 25 PDFs, page-cited digests in the session transcript; an independent
  checker then spot-checked ten of this document's load-bearing claims
  against the primary sources. **Outcome: 8 confirmed, 2
  confirmed-with-correction, 0 refuted**; corrections applied in place
  (LinkFeat FB15k figure was Hits@10 mislabeled as MRR — actual MRR 0.779;
  scope of "beat every learned model" narrowed to FB15k; CSL 100% is
  GCN-specific; GraphGPT's two zero-shot bests come from two different
  variants, std/cot). One process defect the checker caught: the maker had
  pre-labeled §5.2's evidence "checker-verified" before the check ran —
  corrected, and the lesson recorded in `tasks/lessons.md`.
- **Identity/provenance notes (citation hygiene)**: "Training Transformers
  for Mesh-Based Simulations" is a 2025 **preprint under review** (its 38.8%
  and scaling-law claims are medium-low provenance); "A Complete Guide to
  Spherical Equivariant Graph Transformers" is a **Substack-derived
  tutorial** — pedagogy, not evidence; "Regression Language Models for
  Codepdf" (malformed filename) self-declares ICML 2026 and "Knowledge
  Homophily" self-declares WSDM 2026 — venues post-dating our training data,
  unconfirmed; the GNN4TS survey's authorship was inferred from
  acknowledgments (high confidence, not printed on the body pages); DepGraph
  is peer-reviewed (CVPR 2023) but the PDF is the arXiv version.
- **Source internal-inconsistency catalog** (checker-grade cautions before
  any future citation): Cranmer's body text calls Table 1 "fit errors" and
  claims L1 "highest correlations" while its own caption defines R² and its
  own table shows L1 failing both Charge systems — cite the caption reading;
  RLM's "highest average Kendall-τ" rests on a 0.002 margin with baselines
  winning 3 of 5 spaces; DepGraph reports MACs-ratio "speedups" (not
  wall-clock) over mismatched base accuracies; PyTorch Frame's task counts
  disagree between text and figure caption and its Trompt citation resolves
  to the wrong paper; Dwivedi–Bresson's contributions section claims it
  "surpasses baseline isotropic and anisotropic GNNs" while its own Table 2
  shows GatedGCN — an anisotropic baseline — winning all three benchmarks
  (the abstract itself claims only to "close the gap"); GraphGPT's "2–10×"
  is against cross-label-space-handicapped baselines, and its zero-shot
  PubMed/Cora bests come from two different variants merged as "ours".
- **Status discipline**: everything here is `research_only` synthesis;
  finance-transfer claims are extrapolation (`validation_pending`); nothing
  promotes any hypothesis or authorizes any capability.
