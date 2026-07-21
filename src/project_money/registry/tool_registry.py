"""Typed, documented tool registry — the API-first data-access discipline.

Doctrine (synthesis §3.8, §4 tool 8; API-Based Web Agents; HyperAgent):
- every data source is a typed, documented callable tool with a worked example
  per parameter (TOOLMAKER's tool-definition contract);
- two-tier docs: a compact always-in-context ``index()`` plus on-demand
  ``get_docs(name)`` — the pattern that controls context cost at scale;
- **read-only by construction**: the registry structurally refuses any spec
  not marked read-only, and refuses forbidden action words in identifiers
  (label_policy §1). A capability existing is not authorization to use it —
  here, execution-capable specs cannot even be registered.

This is the *framework only*. No live provider adapters exist; registering a
real Tiingo/FRED tool remains gated (see docs/provider_strategy.md) and a
Robinhood tool additionally gated by docs/broker_strategy.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

# label_policy §1 action words forbidden as identifier tokens. Position/Long/
# Short are qualified in the policy ("as an action"/"as a directive") and are
# not identifier-banned. Token-based matching (underscore-split) avoids false
# hits inside larger words while catching e.g. 'order_size', 'entry_scanner'.
_FORBIDDEN_TOKENS = frozenset(
    {"buy", "sell", "trade", "order", "execute", "fill", "entry", "exit", "recommendation"}
)
_SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")


def _forbidden_tokens_in(identifier: str) -> list[str]:
    return sorted(set(identifier.lower().split("_")) & _FORBIDDEN_TOKENS)


@dataclass(frozen=True)
class ParamSpec:
    """One typed parameter with a mandatory worked example (TOOLMAKER contract:
    the example is what admission gates hold out *against* — validation cases
    must differ from it)."""

    name: str
    type_name: str
    description: str
    example: Any

    def validate(self) -> list[str]:
        problems = []
        if not _SNAKE_CASE.match(self.name):
            problems.append(f"param name {self.name!r} is not snake_case")
        bad = _forbidden_tokens_in(self.name)
        if bad:
            problems.append(
                f"param name {self.name!r} contains forbidden action tokens {bad} "
                "(label_policy §1 — field names are identifiers too)"
            )
        if not self.type_name.strip():
            problems.append(f"param {self.name!r} missing type_name")
        if not self.description.strip():
            problems.append(f"param {self.name!r} missing description")
        if self.example is None:
            problems.append(f"param {self.name!r} missing worked example")
        return problems


@dataclass(frozen=True)
class ToolSpec:
    """A registered tool's contract. ``read_only`` must be True — the registry
    rejects anything else (research-only by construction)."""

    name: str
    description: str
    params: tuple[ParamSpec, ...]
    returns: str
    provenance: str = ""
    docs: str = ""
    read_only: bool = True

    def validate(self) -> list[str]:
        problems = []
        if not _SNAKE_CASE.match(self.name):
            problems.append(f"tool name {self.name!r} is not snake_case")
        bad = _forbidden_tokens_in(self.name)
        if bad:
            problems.append(
                f"tool name {self.name!r} contains forbidden action tokens {bad} "
                "(label_policy §1)"
            )
        if not self.description.strip():
            problems.append("description is empty")
        if len(self.description.splitlines()) > 1:
            problems.append("description must be one line (it feeds the compact index)")
        if not self.returns.strip():
            problems.append("returns spec is empty")
        if not self.read_only:
            problems.append(
                "read_only=False is not registrable: this registry only admits "
                "read-only research tools (safety_policy; provider_strategy)"
            )
        for p in self.params:
            problems.extend(p.validate())
        return problems


class ToolRegistry:
    """In-memory registry with two-tier documentation and gated registration.

    ``register`` refuses invalid specs and duplicate names (replacement must be
    explicit — no silent overwrite). An optional ``admission_report`` records
    how the tool was validated (see project_money.toolfactory); tools without
    one are at most provisional and ``index()`` marks them so.
    """

    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}
        self._admission: dict[str, dict[str, Any]] = {}
        self._readiness: dict[str, dict[str, Any]] = {}

    def register(
        self,
        spec: ToolSpec,
        *,
        admission_report: dict[str, Any] | None = None,
        replace: bool = False,
    ) -> None:
        problems = spec.validate()
        if problems:
            raise ValueError(f"spec rejected: {problems}")
        if spec.name in self._specs and not replace:
            raise ValueError(f"tool {spec.name!r} already registered (pass replace=True)")
        self._specs[spec.name] = spec
        if admission_report is not None:
            self._admission[spec.name] = dict(admission_report)
        elif replace:
            self._admission.pop(spec.name, None)
        if replace:
            # a replaced implementation's pre-flight result is meaningless for
            # the new one — stale readiness must not be attributed to it
            self._readiness.pop(spec.name, None)

    # -- two-tier docs --------------------------------------------------------

    def index(self) -> list[str]:
        """Compact tier: one line per tool — name, one-line description, and a
        provisional marker when no admission report exists."""
        lines = []
        for name in sorted(self._specs):
            spec = self._specs[name]
            marker = "" if name in self._admission else " [provisional: no admission report]"
            lines.append(f"{name} — {spec.description}{marker}")
        return lines

    def get_docs(self, name: str) -> str:
        """Full tier: complete signature, per-param examples, returns spec,
        provenance, and any extended docs — fetched on demand."""
        spec = self._lookup(name)
        lines = [
            f"# {spec.name}",
            spec.description,
            "",
            "## Parameters",
        ]
        for p in spec.params:
            lines.append(f"- `{p.name}` ({p.type_name}): {p.description} — example: `{p.example!r}`")
        lines += ["", f"## Returns", spec.returns]
        if spec.provenance:
            lines += ["", f"## Provenance", spec.provenance]
        if spec.docs:
            lines += ["", spec.docs]
        report = self._admission.get(spec.name)
        lines += [
            "",
            "## Admission",
            "validated: " + ("yes" if report else "NO — provisional, do not rely without validation"),
        ]
        return "\n".join(lines)

    # -- lookup & readiness ---------------------------------------------------

    def _lookup(self, name: str) -> ToolSpec:
        if name not in self._specs:
            raise KeyError(f"unknown tool {name!r}; known: {sorted(self._specs)}")
        return self._specs[name]

    def search(self, query: str) -> list[str]:
        """Ranked + previewed search (the affordance the HyperAgent ablation
        showed is worth ~an order of magnitude over bare matching): results
        ordered exact-name > name-prefix > name-substring > description match,
        each line carrying the one-line description as preview."""
        q = query.lower()

        def rank(name: str) -> int | None:
            nl, dl = name.lower(), self._specs[name].description.lower()
            if nl == q:
                return 0
            if nl.startswith(q):
                return 1
            if q in nl:
                return 2
            if q in dl:
                return 3
            return None

        scored = sorted(
            ((r, n) for n in self._specs if (r := rank(n)) is not None),
        )
        return [f"{n} — {self._specs[n].description}" for _, n in scored]

    def find(self, query: str) -> list[str]:
        """Ranked names only (same order as ``search``) — the router's 'does a
        validated tool already exist?' check before building a new one."""
        return [line.split(" — ", 1)[0] for line in self.search(query)]

    def readiness_check(
        self, name: str, checker: Callable[[], tuple[bool, str]]
    ) -> dict[str, Any]:
        """Deterministic pre-flight: is this tool's dependency available?
        (The 'command-not-found' guard — the single largest failure class in
        Terminal-Bench.) ``checker`` returns (ok, detail); the result is
        recorded and returned. No network calls belong in checkers during the
        gated phase — check local caches, env-var presence, file mounts."""
        self._lookup(name)
        ok, detail = checker()
        result = {"ok": bool(ok), "detail": detail}
        self._readiness[name] = result
        return result

    def readiness(self, name: str) -> dict[str, Any] | None:
        return self._readiness.get(name)
