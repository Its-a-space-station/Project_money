import pytest

from project_money.registry import ParamSpec, ToolSpec, ToolRegistry
from project_money.toolfactory import (
    AdmissionCase,
    validate_tool,
    register_validated,
)


def sharpe_like(values: tuple, scale: float = 1.0) -> float:
    """A deterministic toy tool under test."""
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return scale * mean / (var**0.5) if var > 0 else 0.0


CREATION_EXAMPLE = {"values": (1.0, 2.0, 3.0), "scale": 1.0}


class TestValidateTool:
    def test_good_tool_passes(self):
        report = validate_tool(
            sharpe_like,
            CREATION_EXAMPLE,
            [
                AdmissionCase({"values": (2.0, 4.0, 6.0), "scale": 1.0}, expected=2.0),
                AdmissionCase(
                    {"values": (1.0, 1.0, 1.0), "scale": 5.0},
                    predicate=lambda out: None if out == 0.0 else f"expected 0 for constant input, got {out}",
                ),
            ],
        )
        assert report.passed, report.reasons
        assert report.determinism_ok

    def test_no_held_out_cases_fails(self):
        report = validate_tool(sharpe_like, CREATION_EXAMPLE, [])
        assert not report.passed
        assert any("no held-out cases" in r for r in report.reasons)

    def test_creation_example_only_fails(self):
        """The SWE-smith checker-leak guard: validating on what the maker saw
        proves nothing."""
        report = validate_tool(
            sharpe_like, CREATION_EXAMPLE, [AdmissionCase(dict(CREATION_EXAMPLE))]
        )
        assert not report.passed
        assert any("nothing was held out" in r for r in report.reasons)

    def test_silently_wrong_tool_caught_by_known_answer(self):
        """The TOOLMAKER failure mode: plausible output, wrong value."""

        def wrong_tool(values, scale=1.0):
            return sharpe_like(values, scale) * 1.1  # subtly off

        report = validate_tool(
            wrong_tool,
            CREATION_EXAMPLE,
            [AdmissionCase({"values": (2.0, 4.0, 6.0), "scale": 1.0}, expected=2.0)],
        )
        assert not report.passed
        assert any("known-answer mismatch" in r for r in report.reasons)

    def test_nondeterministic_tool_caught(self):
        state = {"n": 0}

        def flaky(values, scale=1.0):
            state["n"] += 1
            return sharpe_like(values, scale) + state["n"] * 1e-3

        report = validate_tool(
            flaky,
            CREATION_EXAMPLE,
            [
                AdmissionCase(
                    {"values": (2.0, 4.0, 6.0), "scale": 1.0},
                    predicate=lambda out: None,  # constrained; determinism still checked
                )
            ],
        )
        assert not report.passed
        assert not report.determinism_ok

    def test_raising_tool_caught(self):
        def broken(values, scale=1.0):
            raise RuntimeError("boom")

        report = validate_tool(
            broken,
            CREATION_EXAMPLE,
            [
                AdmissionCase(
                    {"values": (1.0, 2.0), "scale": 1.0},
                    predicate=lambda out: None,
                )
            ],
        )
        assert not report.passed
        assert any("RuntimeError" in r for r in report.reasons)

    def test_property_checks_apply_to_every_case(self):
        report = validate_tool(
            sharpe_like,
            CREATION_EXAMPLE,
            [AdmissionCase({"values": (-6.0, -4.0, -2.0), "scale": 1.0})],
            property_checks=(
                lambda out: None if out >= 0 else "output must be non-negative",
            ),
        )
        assert not report.passed
        assert any("property check 0" in r for r in report.reasons)


class TestReviewHardening:
    """Regression tests for the adversarial review's confirmed findings."""

    def test_unconstrained_case_fails(self):
        """A case with no expected, no predicate, and no property checks used
        to pass a known-wrong tool — must now fail as vacuous."""

        def wrong_tool(values, scale=1.0):
            return sharpe_like(values, scale) * 1.1

        report = validate_tool(
            wrong_tool,
            CREATION_EXAMPLE,
            [AdmissionCase({"values": (9.0, 4.0, 6.0), "scale": 1.0})],
        )
        assert not report.passed
        assert any("vacuous" in r for r in report.reasons)

    def test_default_omission_does_not_count_as_held_out(self):
        """Same call with a defaulted param omitted normalizes to the creation
        invocation — nothing was held out."""
        report = validate_tool(
            sharpe_like,
            CREATION_EXAMPLE,
            [AdmissionCase({"values": (1.0, 2.0, 3.0)})],  # scale defaults to 1.0
        )
        assert not report.passed
        assert any("nothing was held out" in r for r in report.reasons)

    def test_bool_does_not_match_int_reference(self):
        report = validate_tool(
            lambda x: True,
            {"x": 1},
            [AdmissionCase({"x": 5}, expected=1)],
        )
        assert not report.passed
        assert any("known-answer mismatch" in r for r in report.reasons)

    def test_int_reference_matches_float_within_tolerance(self):
        report = validate_tool(
            lambda x: float(x) + 1e-12,
            {"x": 1},
            [AdmissionCase({"x": 2}, expected=2)],
        )
        assert report.passed, report.reasons

    def test_array_like_outputs_do_not_crash_the_gate(self):
        import pandas as pd

        def frame_tool(n):
            return pd.DataFrame({"a": range(n)})

        report = validate_tool(
            frame_tool,
            {"n": 3},
            [AdmissionCase({"n": 5}, expected=pd.DataFrame({"a": range(5)}))],
        )
        assert report.passed, report.reasons

        report_bad = validate_tool(
            frame_tool,
            {"n": 3},
            [AdmissionCase({"n": 5}, expected=pd.DataFrame({"a": range(4)}))],
        )
        assert not report_bad.passed  # mismatch reported, no crash

    def test_failing_lookahead_check_fails_admission(self):
        class FakeResult:
            passed = False
            reasons = ["cutoff 2020-06-01: weights differ — lookahead"]

        report = validate_tool(
            sharpe_like,
            CREATION_EXAMPLE,
            [AdmissionCase({"values": (2.0, 4.0, 6.0), "scale": 1.0}, expected=2.0)],
            lookahead_check=lambda: FakeResult(),
        )
        assert not report.passed
        assert any("lookahead check failed" in r for r in report.reasons)


class TestRegisterValidated:
    def spec(self):
        return ToolSpec(
            name="sharpe_like",
            description="Toy scaled mean/std ratio on a tuple of values.",
            params=(ParamSpec("values", "tuple[float,...]", "input values", (1.0, 2.0, 3.0)),),
            returns="float",
        )

    def test_passing_report_registers_with_admission(self):
        reg = ToolRegistry()
        report = validate_tool(
            sharpe_like,
            CREATION_EXAMPLE,
            [AdmissionCase({"values": (2.0, 4.0, 6.0), "scale": 1.0}, expected=2.0)],
        )
        register_validated(reg, self.spec(), sharpe_like, report)
        assert "validated: yes" in reg.get_docs("sharpe_like")

    def test_failing_report_refused(self):
        reg = ToolRegistry()
        report = validate_tool(sharpe_like, CREATION_EXAMPLE, [])
        with pytest.raises(ValueError):
            register_validated(reg, self.spec(), sharpe_like, report)
        assert reg.find("sharpe") == []  # nothing slipped through
