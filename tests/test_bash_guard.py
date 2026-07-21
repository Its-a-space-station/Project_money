"""Bracket tests for the Bash findings guard: shell writes into findings/
blocked, reads and unrelated commands allowed."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parent.parent / "hooks" / "guard_findings_bash.py"


def run_guard(command: str, tool_name: str = "Bash") -> subprocess.CompletedProcess:
    payload = {"tool_name": tool_name, "tool_input": {"command": command}}
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


class TestBlocked:
    @pytest.mark.parametrize(
        "cmd",
        [
            "echo '{\"label\": \"paper_candidate\"}' > findings/f.json",
            "printf '%s' data >> findings/f.json",
            "cat notes.json | tee findings/f.json",
            "cp /tmp/x.json findings/f.json",
            "mv draft.json findings/f.json",
            "rm findings/f.json",
            "python3 -c \"open('findings/f.json','w').write('{}')\"",
            "sed -i '' 's/pending/candidate/' findings/f.json",
        ],
    )
    def test_shell_writes_blocked(self, cmd):
        p = run_guard(cmd)
        assert p.returncode == 2, cmd
        assert "Write tool" in p.stderr


class TestAllowed:
    @pytest.mark.parametrize(
        "cmd",
        [
            "ls findings/",
            "cat findings/f.json",
            "grep -r watchlist findings/",
            "git diff findings/",
            "echo hello > /tmp/out.txt",  # write, but not findings
            "pytest tests/",
            # target-aware: these MENTION findings + a write construct but do
            # not write INTO findings/ — must NOT be blocked (the regression
            # that motivated the target-aware rewrite)
            "git commit -m 'guard against shell writes into findings/; generator<->gate'",
            "echo 'no promoted label without an artifact under findings/'",
            "grep -rn 'findings/' docs/ > /tmp/refs.txt",  # redirect to /tmp, not findings
            "cp findings/f.json /tmp/backup.json",  # findings is the SOURCE, not target
        ],
    )
    def test_reads_and_unrelated_allowed(self, cmd):
        p = run_guard(cmd)
        assert p.returncode == 0, (cmd, p.stderr)

    def test_non_bash_tool_ignored(self):
        p = run_guard("anything > findings/f.json", tool_name="Write")
        assert p.returncode == 0
