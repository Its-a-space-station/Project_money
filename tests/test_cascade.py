import pytest

from project_money.validation.cascade import Stage, run_cascade


def passing_stage(name="pass"):
    return Stage(name, lambda c: (True, {"score": 1.0}, []))


def failing_stage(name="fail"):
    return Stage(name, lambda c: (False, {"score": 0.0}, ["threshold not met"]))


def raising_stage(name="boom"):
    def fn(c):
        raise RuntimeError("evaluator crashed")

    return Stage(name, fn)


class TestCascade:
    def test_all_pass_promotes(self):
        result = run_cascade("cand", [passing_stage("s0"), passing_stage("s1")])
        assert result.passed
        assert result.label == "trigger_ready_research_candidate"
        assert result.failed_stage is None

    def test_stops_at_first_failure(self):
        calls = []

        def tracking(name, ok):
            def fn(c):
                calls.append(name)
                return ok, {}, [] if ok else ["nope"]

            return Stage(name, fn)

        result = run_cascade("cand", [tracking("s0", True), tracking("s1", False), tracking("s2", True)])
        assert result.label == "reject"
        assert result.failed_stage == "s1"
        assert calls == ["s0", "s1"]  # expensive s2 never ran

    def test_exception_yields_validation_pending(self):
        result = run_cascade("cand", [passing_stage(), raising_stage()])
        assert result.label == "validation_pending"
        assert not result.passed
        assert any("RuntimeError" in r for r in result.stages[-1].reasons)

    def test_merged_metrics_are_stage_prefixed(self):
        result = run_cascade("cand", [passing_stage("smoke"), passing_stage("full")])
        merged = result.merged_metrics()
        assert merged == {"smoke.score": 1.0, "full.score": 1.0}

    def test_canonical_labels_only(self):
        """No cascade outcome may ever be an action word."""
        for stages in ([passing_stage()], [failing_stage()], [raising_stage()]):
            label = run_cascade("c", stages).label
            assert label in {
                "trigger_ready_research_candidate",
                "reject",
                "validation_pending",
            }
