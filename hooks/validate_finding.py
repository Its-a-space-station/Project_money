#!/usr/bin/env python3
"""PreToolUse hook: no promoted finding without an executed verification artifact.

Enforces "self-attested results are at most validation_pending" (CLAUDE.md
Part I §5) at the file-write boundary. Rules for records under ``findings/``:

- must be a JSON *object* with a canonical ``label`` (label_policy);
- promoted labels (anything beyond validation_pending / needs_human_review /
  reject) require: non-empty ``maker``, non-empty ``verification.checker``
  distinct from maker, and ``verification.artifact_path`` that (a) resolves
  under ``outputs/``, (b) exists, and (c) parses as JSON — the executed
  cascade/falsification output;
- findings are rewritten whole (Write); Edit-family tools are blocked;
- only the exact path ``findings/README.md`` is exempt.

Fail-closed design (post-review hardening): once a write is determined to
target findings/, ANY internal error blocks (exit 2). Path matching is
normalized (relative paths, ``./`` prefixes, case-insensitive — APFS is
case-insensitive) and anchored on CLAUDE_PROJECT_DIR first, session cwd
second; if any interpretation lands in findings/, the gate applies.

Known residual gap (defense in depth, not proof): file writes made through
the Bash tool are covered separately by hooks/guard_findings_bash.py, which
is heuristic; the final gates remain human review and git diff.

Hook protocol: tool-call JSON on stdin; exit 0 allow, exit 2 block (stderr is
the agent-visible message).
"""

from __future__ import annotations

import json
import os
import sys

SELF_ATTESTED_OK = {"validation_pending", "needs_human_review", "reject"}
CANONICAL = SELF_ATTESTED_OK | {
    "watchlist",
    "trigger_ready_research_candidate",
    "paper_candidate",
    "research_only",
}

EDIT_FAMILY = {"Edit", "MultiEdit", "NotebookEdit"}


def block(msg: str) -> None:
    print(f"validate_finding: {msg}", file=sys.stderr)
    sys.exit(2)


def _norm(p: str) -> str:
    return os.path.normpath(p).replace("\\", "/").lower()


def _findings_rel(path: str, roots: list[str]) -> str | None:
    """Return the normalized findings-relative interpretation of ``path`` if
    ANY root-anchored (or raw-relative) reading lands under findings/."""
    candidates: list[str] = []
    if os.path.isabs(path):
        for r in roots:
            if r:
                try:
                    candidates.append(os.path.relpath(path, r))
                except ValueError:
                    pass
    else:
        candidates.append(path)  # raw relative, e.g. './findings/x.json'
        for r in roots:
            if r:
                try:
                    candidates.append(os.path.relpath(os.path.join(r, path), r))
                except ValueError:
                    pass
    for c in candidates:
        n = _norm(c)
        if n == "findings" or n.startswith("findings/"):
            return n
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unparsable hook payload; nothing to judge

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    path = tool_input.get("file_path", "") or ""
    if not path:
        sys.exit(0)

    roots = [os.environ.get("CLAUDE_PROJECT_DIR", ""), payload.get("cwd", "") or ""]

    try:
        rel = _findings_rel(path, roots)
        if rel is None:
            sys.exit(0)
        if rel == "findings/readme.md":  # ONLY the exact top-level README
            sys.exit(0)

        if tool in EDIT_FAMILY:
            block(
                "finding records must be rewritten whole (Write), not partially "
                "edited — a fragment cannot be validated as a record"
            )
        if tool != "Write":
            block(f"tool {tool!r} may not write into findings/ — use Write")

        record = json.loads(tool_input.get("content", ""))
        if not isinstance(record, dict):
            block("finding must be a JSON object (got a non-object JSON value)")

        label = record.get("label")
        if label not in CANONICAL:
            block(
                f"label {label!r} is not canonical; use one of {sorted(CANONICAL)} "
                "(docs/label_policy.md — action words are never labels)"
            )
        if label in SELF_ATTESTED_OK:
            sys.exit(0)

        # --- promotion: full evidence requirements -------------------------
        maker = str(record.get("maker", "") or "")
        verification = record.get("verification") or {}
        if not isinstance(verification, dict):
            block("verification must be an object")
        artifact = str(verification.get("artifact_path", "") or "")
        checker = str(verification.get("checker", "") or "")

        if not maker:
            block(
                f"label {label!r} is a promotion but 'maker' is missing/empty — "
                "maker must be recorded so maker != checker is auditable"
            )
        if not checker:
            block("verification.checker is missing (maker != checker must be recorded)")
        if checker == maker:
            block(
                f"checker {checker!r} equals maker — maker != checker "
                "(docs/maker_checker_policy.md)"
            )
        if not artifact:
            block(
                f"label {label!r} is a promotion but verification.artifact_path is "
                "missing — self-attested results are at most validation_pending"
            )

        # artifact must resolve under outputs/ of a known root and parse as JSON
        art_abs = None
        if os.path.isabs(artifact):
            for r in roots:
                if r:
                    try:
                        if _norm(os.path.relpath(artifact, r)).startswith("outputs/"):
                            art_abs = artifact
                            break
                    except ValueError:
                        pass
        else:
            if _norm(artifact).startswith("outputs/"):
                base = next((r for r in roots if r), os.getcwd())
                art_abs = os.path.join(base, artifact)
        if art_abs is None:
            block(
                f"verification.artifact_path {artifact!r} must live under outputs/ "
                "(the executed verification output directory)"
            )
        if not os.path.exists(art_abs):
            block(
                f"verification.artifact_path {artifact!r} does not exist — the "
                "verification must have been EXECUTED before the label is claimed"
            )
        try:
            with open(art_abs, encoding="utf-8") as fh:
                json.load(fh)
        except Exception:
            block(
                f"verification artifact {artifact!r} is not parseable JSON — an "
                "executed cascade/falsification result is machine-readable"
            )

        sys.exit(0)

    except SystemExit:
        raise
    except Exception as exc:  # fail CLOSED for findings writes
        block(f"internal error ({type(exc).__name__}: {exc}) — failing closed")


if __name__ == "__main__":
    main()
