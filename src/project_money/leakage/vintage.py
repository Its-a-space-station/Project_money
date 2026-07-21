"""Temporal decontamination auditing — the backtest-lookahead analogue of
SWE-rebench's issue-date vs model-release tracking.

Every dataset/tool used in an evaluation carries a vintage record; the audit
compares those vintages (and any model knowledge cutoffs) against the claimed
out-of-sample window and the hypothesis formation date, labeling each metric
``clean`` or ``contaminated`` with explicit reasons. Contaminated results are
not deleted — they are labeled, so reports can carry the flag (never silent).

Research-only: this audits evidence quality; it takes no action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class VintageRecord:
    """Provenance stamp for one data/tool dependency of an evaluation.

    - ``vintage_date``: when this dataset snapshot was assembled/published.
      A dataset assembled *after* the OOS window closes may embed revisions,
      survivorship filtering, or symbol-set choices informed by that window.
    - ``knowledge_cutoff``: for model/LLM dependencies — training cutoff; None
      for plain data.
    - ``point_in_time``: True if the source is a certified point-in-time /
      as-reported archive (exempts the vintage-after-OOS rule).
    """

    source_id: str
    vintage_date: date
    knowledge_cutoff: date | None = None
    point_in_time: bool = False
    notes: str = ""


@dataclass
class AuditFinding:
    source_id: str
    status: str  # "clean" | "contaminated"
    reasons: list[str] = field(default_factory=list)


def audit_vintages(
    records: list[VintageRecord],
    *,
    oos_start: date,
    oos_end: date,
    formation_date: date,
) -> tuple[str, list[AuditFinding]]:
    """Audit every dependency of an evaluation against its OOS window.

    Rules (each violation recorded, none fatal to the audit itself):
    1. A non-point-in-time dataset with ``vintage_date`` after ``oos_start``
       may embed the OOS period (revisions/survivorship) → contaminated.
    2. A model whose ``knowledge_cutoff`` falls after ``oos_start`` has seen
       the "out-of-sample" period in training → contaminated.
    3. A hypothesis formed after the OOS window closed (``formation_date`` >
       ``oos_end``) is flagged on every source: the window predates the idea,
       so it is in-sample-by-selection unless a fresh window is used.

    Returns ``(overall_status, findings)`` where overall is "clean" only if
    every finding is clean.
    """
    if oos_end < oos_start:
        raise ValueError("oos_end precedes oos_start")

    findings: list[AuditFinding] = []
    hypothesis_after_window = formation_date > oos_end

    for rec in records:
        reasons: list[str] = []
        if not rec.point_in_time and rec.vintage_date > oos_start:
            reasons.append(
                f"dataset vintage {rec.vintage_date.isoformat()} postdates OOS start "
                f"{oos_start.isoformat()} and source is not point-in-time"
            )
        if rec.knowledge_cutoff is not None and rec.knowledge_cutoff > oos_start:
            reasons.append(
                f"model knowledge cutoff {rec.knowledge_cutoff.isoformat()} postdates "
                f"OOS start {oos_start.isoformat()} — 'out-of-sample' was in training data"
            )
        if hypothesis_after_window:
            reasons.append(
                f"hypothesis formation {formation_date.isoformat()} postdates OOS end "
                f"{oos_end.isoformat()} — window predates the idea (selection risk); "
                "use a fresh window"
            )
        findings.append(
            AuditFinding(rec.source_id, "contaminated" if reasons else "clean", reasons)
        )

    overall = "clean" if all(f.status == "clean" for f in findings) else "contaminated"
    return overall, findings
