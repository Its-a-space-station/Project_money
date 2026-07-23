from datetime import date

import pytest

from project_money.leakage import VintageRecord, audit_vintages
from tests.specimens import marketsenseai_vintage_records

OOS_START = date(2024, 1, 1)
OOS_END = date(2024, 12, 31)
FORMED = date(2023, 6, 1)


class TestVintageAudit:
    def test_clean_case(self):
        recs = [VintageRecord("prices_v1", vintage_date=date(2023, 12, 15))]
        overall, findings = audit_vintages(
            recs, oos_start=OOS_START, oos_end=OOS_END, formation_date=FORMED
        )
        assert overall == "clean"
        assert findings[0].status == "clean"

    def test_late_vintage_contaminated(self):
        recs = [VintageRecord("prices_v2", vintage_date=date(2025, 3, 1))]
        overall, findings = audit_vintages(
            recs, oos_start=OOS_START, oos_end=OOS_END, formation_date=FORMED
        )
        assert overall == "contaminated"
        assert any("postdates OOS start" in r for r in findings[0].reasons)

    def test_point_in_time_exemption(self):
        recs = [
            VintageRecord("pit_archive", vintage_date=date(2025, 3, 1), point_in_time=True)
        ]
        overall, _ = audit_vintages(
            recs, oos_start=OOS_START, oos_end=OOS_END, formation_date=FORMED
        )
        assert overall == "clean"

    def test_model_knowledge_cutoff_contaminated(self):
        recs = [
            VintageRecord(
                "llm_features",
                vintage_date=date(2023, 1, 1),
                knowledge_cutoff=date(2024, 6, 1),
            )
        ]
        overall, findings = audit_vintages(
            recs, oos_start=OOS_START, oos_end=OOS_END, formation_date=FORMED
        )
        assert overall == "contaminated"
        assert any("knowledge cutoff" in r for r in findings[0].reasons)

    def test_hypothesis_formed_after_window_flagged(self):
        recs = [VintageRecord("prices_v1", vintage_date=date(2023, 12, 15))]
        overall, findings = audit_vintages(
            recs,
            oos_start=OOS_START,
            oos_end=OOS_END,
            formation_date=date(2025, 6, 1),  # idea came after the window closed
        )
        assert overall == "contaminated"
        assert any("selection risk" in r for r in findings[0].reasons)

    def test_bad_window_raises(self):
        with pytest.raises(ValueError):
            audit_vintages([], oos_start=OOS_END, oos_end=OOS_START, formation_date=FORMED)


class TestSpecimenCoverage:
    """§9 known-bad specimens the vintage auditor must reject (calibration-first)."""

    def test_marketsenseai_time_travel_contaminated(self):
        # An LLM whose knowledge cutoff (2024-06) postdates the OOS start it is
        # 'predicting' — the MarketSenseAI time-travel pattern (S3).
        overall, findings = audit_vintages(
            marketsenseai_vintage_records(),
            oos_start=OOS_START,
            oos_end=OOS_END,
            formation_date=FORMED,
        )
        assert overall == "contaminated"
        assert any("knowledge cutoff" in r for f in findings for r in f.reasons)
