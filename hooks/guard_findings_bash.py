#!/usr/bin/env python3
"""PreToolUse hook (Bash): close the shell end-run around the findings gate.

hooks/validate_finding.py validates findings written via Write; this guard
blocks Bash commands that *write into* findings/ (redirection, tee, cp/mv/ln,
rm, in-place sed, inline python writers), which would otherwise bypass
validation entirely.

Detection is **target-aware**, not keyword co-occurrence: a command is blocked
only when a write construct actually references a ``findings/`` path as its
target. Commands that merely mention "findings" (a git commit message, an echo,
a grep) are NOT blocked — that earlier over-broad heuristic false-positived on
routine git operations.

Heuristic by necessity (no full shell parse): it errs toward precision, so it
can miss an exotic write path. This is defense in depth, not proof — the final
gates remain human review and ``git diff`` before any findings/ commit.

Exit 0 allow, exit 2 block.
"""

from __future__ import annotations

import json
import re
import sys

# A findings path fragment: optional quote, optional ./, then findings/ .
_FIND = r"""['"]?(?:\./)?findings/"""

# Each pattern describes a WRITE whose target is a findings/ path.
# For cp/mv/ln/install/rsync the write target is the LAST path argument, so
# findings/ must sit at the end of the command segment to count as a target
# (findings/ as a SOURCE, e.g. `cp findings/f.json /tmp/x`, is not blocked).
_WRITE_TO_FINDINGS = [
    rf">>?\s*{_FIND}",                                   # echo ... > findings/x  /  >> findings/x
    rf"\btee\b\s+(?:-a\s+)?{_FIND}",                     # ... | tee findings/x
    rf"\b(?:cp|mv|ln|install|rsync)\b[^|&;]*\s{_FIND}\S*\s*(?:$|[|&;])",  # ... DST=findings/x
    rf"\brm\b[^|&;]*?\s{_FIND}",                          # rm findings/x (target either position)
    rf"\btouch\b[^|&;]*?\s{_FIND}",                       # touch findings/x
    rf"\bsed\b[^|&;]*?-i[^|&;]*?{_FIND}",                # sed -i ... findings/x
    rf"\bdd\b[^|&;]*?of=\s*{_FIND}",                     # dd of=findings/x
    rf"""open\(\s*['"](?:\./)?findings/[^'"]*['"]\s*,\s*['"][wax]""",  # open('findings/..','w')
    rf"(?:to_json|to_csv|write_text|write_bytes|savetxt|dump)\([^)]*{_FIND}",  # py writers
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _WRITE_TO_FINDINGS]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name", "") != "Bash":
        sys.exit(0)
    command = (payload.get("tool_input", {}) or {}).get("command", "") or ""

    for pattern in _COMPILED:
        if pattern.search(command):
            print(
                "guard_findings_bash: this command appears to WRITE into "
                "findings/ via the shell, which bypasses the promotion gate. "
                "Write finding records with the Write tool (validated by "
                "hooks/validate_finding.py). Read-only inspection of findings/ "
                "is fine.",
                file=sys.stderr,
            )
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
