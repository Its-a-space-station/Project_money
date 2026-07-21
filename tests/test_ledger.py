import pytest

from project_money.ledger import HypothesisLedger, LedgerEntry, param_distance


def entry(i, family="momentum", status="proposed", params=None, ts="2026-07-20T00:00:00"):
    return LedgerEntry(
        entry_id=f"h{i}",
        ts=ts,
        family=family,
        hypothesis=f"hypothesis {i}",
        params=params or {"lookback": 20.0 + i, "threshold": 0.5},
        status=status,
    )


class TestParamDistance:
    def test_identity_is_zero(self):
        p = {"a": 1.0, "b": 2.0}
        assert param_distance(p, p) == 0.0

    def test_missing_key_counts_full(self):
        assert param_distance({"a": 1.0}, {"b": 1.0}) == 1.0

    def test_bounded_and_symmetric(self):
        a, b = {"a": 1.0, "b": 100.0}, {"a": 2.0, "b": 1.0}
        d1, d2 = param_distance(a, b), param_distance(b, a)
        assert d1 == d2
        assert 0.0 <= d1 <= 1.0


class TestLedger:
    def test_roundtrip(self, tmp_path):
        path = tmp_path / "ledger.jsonl"
        led = HypothesisLedger(path)
        led.append(entry(1))
        led.append(entry(2))
        reopened = HypothesisLedger(path)
        assert [e.entry_id for e in reopened.entries] == ["h1", "h2"]

    def test_append_only_updates(self, tmp_path):
        led = HypothesisLedger(tmp_path / "l.jsonl")
        led.append(entry(1, status="proposed"))
        led.append(entry(1, status="reject"))
        assert len(led.entries) == 2  # history preserved
        assert led.latest_by_id()["h1"].status == "reject"

    def test_n_trials_counts_distinct_ids(self, tmp_path):
        led = HypothesisLedger(tmp_path / "l.jsonl")
        led.append(entry(1, status="proposed"))
        led.append(entry(1, status="reject"))  # same trial, updated
        led.append(entry(2))
        led.append(entry(3, family="meanrev"))
        assert led.n_trials() == 3
        assert led.n_trials("momentum") == 2
        assert led.n_trials("meanrev") == 1

    def test_discarded_history(self, tmp_path):
        led = HypothesisLedger(tmp_path / "l.jsonl")
        led.append(entry(1, status="reject"))
        led.append(entry(2, status="discarded"))
        led.append(entry(3, status="watchlist"))
        ids = {e.entry_id for e in led.discarded()}
        assert ids == {"h1", "h2"}

    def test_tabu_detects_near_duplicate(self, tmp_path):
        led = HypothesisLedger(tmp_path / "l.jsonl")
        led.append(entry(1, params={"lookback": 20.0, "threshold": 0.5}))
        tabu, match = led.is_tabu({"lookback": 20.5, "threshold": 0.5}, threshold=0.1)
        assert tabu and match == "h1"
        tabu2, _ = led.is_tabu({"lookback": 200.0, "threshold": 5.0}, threshold=0.1)
        assert not tabu2

    def test_repeat_failure_count_feeds_freeze_rule(self, tmp_path):
        led = HypothesisLedger(tmp_path / "l.jsonl")
        for i in range(3):
            led.append(
                LedgerEntry(
                    entry_id=f"h{i}",
                    ts="2026-07-20T00:00:00",
                    family="momentum",
                    hypothesis="same idea again",
                    params={"lookback": 20.0 + 0.1 * i, "threshold": 0.5},
                    status="reject",
                )
            )
        n = led.repeat_failure_count({"lookback": 20.0, "threshold": 0.5}, threshold=0.1)
        assert n >= 3  # Bilevel freeze rule triggers

    def test_non_canonical_status_rejected(self):
        with pytest.raises(ValueError):
            LedgerEntry(
                entry_id="x",
                ts="2026-07-20T00:00:00",
                family="f",
                hypothesis="h",
                status="buy",  # forbidden action word — must raise
            )

    def test_expected_max_null_sharpe_grows_with_trials(self, tmp_path):
        led = HypothesisLedger(tmp_path / "l.jsonl")
        led.append(entry(1))
        bar1 = led.expected_max_null_sharpe()
        for i in range(2, 101):
            led.append(entry(i))
        bar100 = led.expected_max_null_sharpe()
        assert bar100 > bar1 >= 0.0
        assert bar100 > 1.0  # 100 zero-edge trials produce a >1 best Sharpe bar
