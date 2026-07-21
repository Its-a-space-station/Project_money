"""The finding-validation hook gets the same bracket treatment as every gate:
known-good writes must pass, known-bad writes must block."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "validate_finding.py"


def run_hook(payload: dict, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def write_payload(path: str, record: dict | str, cwd: str) -> dict:
    content = record if isinstance(record, str) else json.dumps(record)
    return {
        "tool_name": "Write",
        "tool_input": {"file_path": path, "content": content},
        "cwd": cwd,
    }


@pytest.fixture()
def project(tmp_path):
    (tmp_path / "findings").mkdir()
    (tmp_path / "outputs").mkdir()
    (tmp_path / "outputs" / "cascade_result.json").write_text("{}")
    return tmp_path


class TestNonFindingPathsUntouched:
    def test_other_files_pass(self, project):
        p = run_hook(
            write_payload(str(project / "docs" / "x.md"), "anything", str(project)),
            str(project),
        )
        assert p.returncode == 0

    def test_findings_readme_exempt(self, project):
        p = run_hook(
            write_payload(str(project / "findings" / "README.md"), "docs", str(project)),
            str(project),
        )
        assert p.returncode == 0


class TestSelfAttestedAllowed:
    @pytest.mark.parametrize("label", ["validation_pending", "needs_human_review", "reject"])
    def test_self_attested_labels_pass_without_artifact(self, project, label):
        record = {"id": "x", "label": label, "maker": "strategy-analyst"}
        p = run_hook(
            write_payload(str(project / "findings" / "f1.json"), record, str(project)),
            str(project),
        )
        assert p.returncode == 0, p.stderr


class TestPromotionsGated:
    def promoted(self, **kw):
        base = {
            "id": "x",
            "label": "trigger_ready_research_candidate",
            "maker": "strategy-analyst",
            "verification": {
                "artifact_path": "outputs/cascade_result.json",
                "checker": "research-validator",
            },
        }
        base.update(kw)
        return base

    def test_valid_promotion_passes(self, project):
        p = run_hook(
            write_payload(str(project / "findings" / "f.json"), self.promoted(), str(project)),
            str(project),
        )
        assert p.returncode == 0, p.stderr

    def test_missing_artifact_blocked(self, project):
        rec = self.promoted(verification={"checker": "research-validator", "artifact_path": ""})
        p = run_hook(
            write_payload(str(project / "findings" / "f.json"), rec, str(project)),
            str(project),
        )
        assert p.returncode == 2
        assert "validation_pending" in p.stderr

    def test_nonexistent_artifact_blocked(self, project):
        rec = self.promoted(
            verification={"artifact_path": "outputs/nope.json", "checker": "research-validator"}
        )
        p = run_hook(
            write_payload(str(project / "findings" / "f.json"), rec, str(project)),
            str(project),
        )
        assert p.returncode == 2
        assert "EXECUTED" in p.stderr

    def test_maker_equals_checker_blocked(self, project):
        rec = self.promoted(
            maker="strategy-analyst",
            verification={
                "artifact_path": "outputs/cascade_result.json",
                "checker": "strategy-analyst",
            },
        )
        p = run_hook(
            write_payload(str(project / "findings" / "f.json"), rec, str(project)),
            str(project),
        )
        assert p.returncode == 2
        assert "maker" in p.stderr

    def test_non_canonical_label_blocked(self, project):
        rec = {"id": "x", "label": "strong_buy"}
        p = run_hook(
            write_payload(str(project / "findings" / "f.json"), rec, str(project)),
            str(project),
        )
        assert p.returncode == 2
        assert "not canonical" in p.stderr

    def test_non_json_blocked(self, project):
        p = run_hook(
            write_payload(str(project / "findings" / "f.json"), "not json", str(project)),
            str(project),
        )
        assert p.returncode == 2

    def test_partial_edit_blocked(self, project):
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(project / "findings" / "f.json"),
                "old_string": "validation_pending",
                "new_string": "trigger_ready_research_candidate",
            },
            "cwd": str(project),
        }
        p = run_hook(payload, str(project))
        assert p.returncode == 2
        assert "rewritten whole" in p.stderr


class TestReviewHardening:
    """Regression tests for the adversarial review's confirmed findings."""

    def promoted(self, **kw):
        base = {
            "id": "x",
            "label": "trigger_ready_research_candidate",
            "maker": "strategy-analyst",
            "verification": {
                "artifact_path": "outputs/cascade_result.json",
                "checker": "research-validator",
            },
        }
        base.update(kw)
        return base

    def test_missing_maker_blocked(self, project):
        rec = self.promoted()
        del rec["maker"]
        p = run_hook(write_payload(str(project / "findings" / "f.json"), rec, str(project)), str(project))
        assert p.returncode == 2
        assert "maker" in p.stderr

    def test_empty_maker_blocked(self, project):
        rec = self.promoted(maker="")
        p = run_hook(write_payload(str(project / "findings" / "f.json"), rec, str(project)), str(project))
        assert p.returncode == 2

    def test_relative_dot_path_gated(self, project):
        """'./findings/x.json' must not slip past the prefix check."""
        rec = {"id": "x", "label": "strong_buy"}
        payload = write_payload("./findings/f.json", rec, str(project))
        p = run_hook(payload, str(project))
        assert p.returncode == 2

    def test_case_insensitive_prefix_gated(self, project):
        """'Findings/' targets the same APFS directory — must be gated."""
        rec = {"id": "x", "label": "strong_buy"}
        p = run_hook(
            write_payload(str(project / "Findings" / "f.json"), rec, str(project)),
            str(project),
        )
        assert p.returncode == 2

    def test_cwd_subdirectory_gated_via_env(self, project):
        """Session launched from a subdir: CLAUDE_PROJECT_DIR anchors the check."""
        import os
        sub = project / "notebooks"
        sub.mkdir()
        rec = {"id": "x", "label": "strong_buy"}
        payload = write_payload(str(project / "findings" / "f.json"), rec, str(sub))
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
        p = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=str(sub),
            env=env,
        )
        assert p.returncode == 2

    def test_non_object_json_blocked(self, project):
        for content in ("[]", "null", '"watchlist"'):
            p = run_hook(
                write_payload(str(project / "findings" / "f.json"), content, str(project)),
                str(project),
            )
            assert p.returncode == 2, content

    def test_artifact_outside_outputs_blocked(self, project):
        (project / "README.md").write_text("hi")
        rec = self.promoted(
            verification={"artifact_path": "README.md", "checker": "research-validator"}
        )
        p = run_hook(write_payload(str(project / "findings" / "f.json"), rec, str(project)), str(project))
        assert p.returncode == 2
        assert "outputs/" in p.stderr

    def test_non_json_artifact_blocked(self, project):
        (project / "outputs" / "junk.txt").write_text("not json")
        rec = self.promoted(
            verification={"artifact_path": "outputs/junk.txt", "checker": "research-validator"}
        )
        p = run_hook(write_payload(str(project / "findings" / "f.json"), rec, str(project)), str(project))
        assert p.returncode == 2
        assert "parseable JSON" in p.stderr

    def test_readme_suffix_no_longer_exempt(self, project):
        p = run_hook(
            write_payload(
                str(project / "findings" / "momentum_README.md"),
                '{"label": "strong_buy"}',
                str(project),
            ),
            str(project),
        )
        assert p.returncode == 2

    def test_exact_readme_still_exempt(self, project):
        p = run_hook(
            write_payload(str(project / "findings" / "README.md"), "docs text", str(project)),
            str(project),
        )
        assert p.returncode == 0

    def test_multiedit_blocked(self, project):
        payload = {
            "tool_name": "MultiEdit",
            "tool_input": {"file_path": str(project / "findings" / "f.json")},
            "cwd": str(project),
        }
        p = run_hook(payload, str(project))
        assert p.returncode == 2
