# Object Memory & Ordering Rules

> Operational rules for how research state is stored, referenced, ordered, and
> compressed. Derived from the memory/relational cluster of
> [agent_tooling_synthesis.md](agent_tooling_synthesis.md) (§3.10, §6.6);
> helpers live in `src/project_money/memory/`. Documentation + code contract —
> not executable automation. Research-only.

## 1. Slots, not blobs

Research state is a set of **discrete, addressable objects** — evidence
records, belief cards, finding records, ledger entries (shapes in
[../schemas/](../schemas/)). Never a single narrative state blob:
compartmentalized objects *plus an explicit interaction step* beat both mashed
summaries and inert stores (RMC's ~91% vs ~30% separation).

## 2. Pointers, not paraphrase

Objects are referenced by **stable content-derived ids**
(`project_money.memory.stable_id`) and paths. An agent citing a record quotes
its id; it never re-describes the content from memory (Pointer-Networks rule:
outputs map back to inputs exactly — paraphrase is where drift enters).

## 3. Erase-then-add writes

Updates are **field-level and non-destructive** (NTM's gated write): edit the
targeted fields, keep unaddressed content, and for append-only stores (the
hypothesis ledger, lessons) never rewrite history — append the new state.
Findings are the exception with a reason: they are rewritten whole so the
promotion hook can validate a complete record.

## 4. One canonical order per set — and order-invariant reads

Every stored/emitted set (watchlists, candidate rankings, evidence lists) has
ONE documented sort key, applied with `canonical_sort` (total order;
stable-id tie-break). Empirically order changes results even when theory says
it shouldn't (Order Matters: same distribution, different order, worse
learning) — so we shrink the equivalence class to a single ordering.

Reads/aggregations over a set must be **order-invariant** (sum/attention-style
reductions, not first-k). Verify with `order_invariant_digest`: the digest of
what a consumer used must equal the digest of the canonical set.

## 5. Protected durable channel

Lossy operations — summarization, pruning, context compression — apply **only
to transient within-session working state, never to the durable cross-session
channel** (belief cards, ledger, lessons, STATE). The RNN-regularization
lesson: corrupting the long-horizon channel is precisely what destroys
retention across sessions. If a durable record must shrink, the compression is
a reviewed change, and what was dropped is listed (evidence-representation
doctrine: never compress away correctness-controlling detail).

## 6. Identity-default plug-ins

A new pipeline stage/component starts as a **pass-through** on a protected
baseline path and earns its keep as an additive correction under an
equal-budget comparison (ResNet/Identity-Mappings/dilated-init doctrine). No
multiplicative meddling with the baseline path.

## 7. Alignment artifacts

Any evidence-weighting model stores *which inputs drove which output* per run
(the Bahdanau α-matrix as a stored research artifact) — attribution is a
deliverable, not an afterthought, and reports cite it by pointer.

## 8. Relations are first-class (future)

Cross-asset structure, when built, follows the MPNN reference design: nodes =
assets, **typed directed edges** = relationships (sector, correlation,
lead-lag), message/update/readout with a permutation-invariant readout, a
master node for one-hop global context. Query-conditioned relations
(RN's g(o_i, o_j, q)). Gated behind its own authorization like all modeling
work.
