import itertools

import pytest

from project_money.memory import canonical_sort, order_invariant_digest, stable_id

RECORDS = [
    {"family": "momentum", "score": 1.2, "id": "a"},
    {"family": "momentum", "score": 0.8, "id": "b"},
    {"family": "meanrev", "score": 1.2, "id": "c"},
    {"family": "meanrev", "score": 1.2, "id": "d"},  # ties on both keys
]


class TestStableId:
    def test_content_derived_and_stable(self):
        a = stable_id({"x": 1, "y": [1, 2]})
        b = stable_id({"y": [1, 2], "x": 1})  # key order irrelevant
        assert a == b and len(a) == 12

    def test_different_content_different_id(self):
        assert stable_id({"x": 1}) != stable_id({"x": 2})


class TestCanonicalSort:
    def test_total_deterministic_order_under_any_permutation(self):
        baseline = canonical_sort(RECORDS, keys=("family", "score"))
        for perm in itertools.permutations(RECORDS):
            assert canonical_sort(list(perm), keys=("family", "score")) == baseline

    def test_ties_broken_deterministically(self):
        out = canonical_sort(RECORDS, keys=("family", "score"))
        tied = [r for r in out if r["family"] == "meanrev" and r["score"] == 1.2]
        assert len(tied) == 2  # both present, in one fixed order via stable_id

    def test_missing_key_raises(self):
        with pytest.raises(KeyError):
            canonical_sort([{"family": "momentum"}], keys=("family", "score"))


class TestReviewHardening:
    """Regression tests for the adversarial review's confirmed findings."""

    def test_numeric_keys_sort_numerically(self):
        """2.0 must sort before 10.0 (string sort put 10 first); -5 before -1."""
        records = [
            {"score": 10.0, "id": "a"},
            {"score": 2.0, "id": "b"},
            {"score": -1.0, "id": "c"},
            {"score": -5.0, "id": "d"},
        ]
        out = canonical_sort(records, keys=("score",))
        assert [r["score"] for r in out] == [-5.0, -1.0, 2.0, 10.0]

    def test_mixed_type_dict_keys_no_crash(self):
        """stable_id/canonical_sort must not raise on int-keyed nested dicts."""
        rec = {"family": "x", "scores": {2020: 1.1, "total": 2.0}}
        assert len(stable_id(rec)) == 12
        out = canonical_sort([rec, {"family": "a", "scores": {}}], keys=("family",))
        assert out[0]["family"] == "a"


class TestOrderInvariantDigest:
    def test_identical_for_any_permutation(self):
        base = order_invariant_digest(RECORDS)
        for perm in itertools.permutations(RECORDS):
            assert order_invariant_digest(list(perm)) == base

    def test_sensitive_to_content(self):
        changed = [dict(RECORDS[0], score=9.9)] + RECORDS[1:]
        assert order_invariant_digest(changed) != order_invariant_digest(RECORDS)
