"""Append-only hypothesis ledger — the trial registry that multiplicity
accounting requires, plus tabu memory against proposal determinism.

Doctrine (synthesis §3.3, §5, §4 tool 5):
- every hypothesis ever evaluated is recorded with outcome and score delta —
  untracked trials silently inflate every Sharpe; ``n_trials`` feeds
  ``validation.metrics.deflated_sharpe``;
- a proposer must consult the DISCARDED history and differentiate (EvoSkill's
  feedback history H);
- tabu memory over recently-tried parameter regions breaks LLM proposal
  determinism (Bilevel's 22-consecutive-identical-discards pathology).

Storage is a JSONL file: append-only, human-readable, git-diffable. Timestamps
are supplied by the caller (no hidden clock reads inside the library —
determinism and replayability).

Research-only: entries describe hypotheses and research outcomes using the
canonical labels; nothing here is a directive to act.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

CANONICAL_STATUSES = {
    "proposed",
    "reject",
    "watchlist",
    "trigger_ready_research_candidate",
    "needs_human_review",
    "paper_candidate",
    "research_only",
    "validation_pending",
    "discarded",
}


@dataclass
class LedgerEntry:
    """One hypothesis trial. ``params`` is a flat dict of the tunable knobs;
    ``family`` groups related hypotheses for per-family trial counts."""

    entry_id: str
    ts: str  # ISO timestamp, caller-supplied
    family: str
    hypothesis: str
    params: dict[str, float] = field(default_factory=dict)
    status: str = "proposed"
    scores: dict[str, float] = field(default_factory=dict)
    parent_id: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.status not in CANONICAL_STATUSES:
            raise ValueError(
                f"status {self.status!r} not in canonical set {sorted(CANONICAL_STATUSES)}"
            )


def param_distance(a: dict[str, float], b: dict[str, float]) -> float:
    """Normalized distance between two parameter dicts.

    Union of keys; missing keys count as maximally different (1.0 per key).
    Per-key difference is |a-b| / (|a| + |b|), bounded to [0, 1]. The mean over
    keys gives a scale-free distance in [0, 1].
    """
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    total = 0.0
    for k in keys:
        if k not in a or k not in b:
            total += 1.0
            continue
        va, vb = float(a[k]), float(b[k])
        denom = abs(va) + abs(vb)
        total += 0.0 if denom == 0 else min(1.0, abs(va - vb) / denom)
    return total / len(keys)


class HypothesisLedger:
    """Append-only JSONL ledger with trial counting and tabu queries."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[LedgerEntry] = []
        if self.path.exists():
            with self.path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        self._entries.append(LedgerEntry(**json.loads(line)))

    # -- write path -----------------------------------------------------------

    def append(self, entry: LedgerEntry) -> None:
        """Append one entry. Existing ids may recur only as status updates —
        an update is a NEW line (append-only history), never a rewrite."""
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
        self._entries.append(entry)

    # -- read path ------------------------------------------------------------

    @property
    def entries(self) -> list[LedgerEntry]:
        return list(self._entries)

    def latest_by_id(self) -> dict[str, LedgerEntry]:
        """Last-written entry per entry_id (the current state of each trial)."""
        out: dict[str, LedgerEntry] = {}
        for e in self._entries:
            out[e.entry_id] = e
        return out

    def n_trials(self, family: str | None = None) -> int:
        """Number of distinct trials (entry_ids), optionally per family — the
        input to deflated-Sharpe multiplicity correction. Every id ever
        proposed counts: abandoned trials still spent the multiple-testing
        budget."""
        seen = {
            e.entry_id
            for e in self._entries
            if family is None or e.family == family
        }
        return len(seen)

    def discarded(self, family: str | None = None) -> list[LedgerEntry]:
        """Current-state entries with status ``discarded`` or ``reject`` — the
        history a proposer must differentiate against."""
        return [
            e
            for e in self.latest_by_id().values()
            if e.status in ("discarded", "reject")
            and (family is None or e.family == family)
        ]

    def is_tabu(
        self,
        params: dict[str, float],
        *,
        recent_k: int = 20,
        threshold: float = 0.1,
    ) -> tuple[bool, str | None]:
        """True if ``params`` is within ``threshold`` distance of any of the
        last ``recent_k`` trials' params — the proposal-determinism breaker.
        Returns (tabu, matching_entry_id)."""
        recent = self._entries[-recent_k:]
        for e in reversed(recent):
            if e.params and param_distance(params, e.params) <= threshold:
                return True, e.entry_id
        return False, None

    def repeat_failure_count(self, params: dict[str, float], *, threshold: float = 0.1) -> int:
        """How many current-state discarded/rejected trials sit within
        ``threshold`` of ``params`` — feeds a freeze rule (Bilevel: freeze a
        direction proposed >=3 times with zero net improvement)."""
        return sum(
            1
            for e in self.discarded()
            if e.params and param_distance(params, e.params) <= threshold
        )

    def recorded_sharpes(
        self, family: str | None = None, *, score_key: str = "sharpe_net"
    ) -> list[float]:
        """Per-trial annualized Sharpe estimates from the ledger (current
        state per trial) — the ``trial_sharpes`` input the corrected deflated-
        Sharpe benchmark requires (empirical cross-trial variance; de Prado's
        Third Law: report every trial)."""
        out = []
        for e in self.latest_by_id().values():
            if family is not None and e.family != family:
                continue
            v = e.scores.get(score_key)
            if v is not None and isinstance(v, (int, float)):
                out.append(float(v))
        return out

    def expected_max_null_sharpe(self, family: str | None = None, *, n_periods: int = 252) -> float:
        """Convenience: the expected best annualized Sharpe among this many
        zero-edge trials (the bar a champion must beat; see
        validation.metrics.deflated_sharpe for the full probability)."""
        n = max(1, self.n_trials(family))
        if n == 1:
            return 0.0
        from statistics import NormalDist

        gamma = 0.5772156649015329
        nd = NormalDist()
        z1 = nd.inv_cdf(1.0 - 1.0 / n)
        z2 = nd.inv_cdf(1.0 - 1.0 / (n * math.e))
        sr_std = math.sqrt(1.0 / n_periods)
        per_period = sr_std * ((1.0 - gamma) * z1 + gamma * z2)
        return per_period * math.sqrt(252)
