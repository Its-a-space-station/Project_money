"""Canonical ordering + stable pointers for research object sets.

Doctrine (synthesis §3.10; Order Matters / Pointer Networks / RN):
- every stored or emitted set gets ONE canonical order (documented sort key) —
  order changes model behavior even when theory says it shouldn't;
- reads/aggregations must be order-invariant — verified with a digest that is
  identical for any permutation of the same records;
- objects are referenced by stable content-derived IDs (pointers), never
  paraphrased.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Sequence


def _stringify_keys(obj: Any) -> Any:
    """Recursively coerce dict keys to str so canonical JSON never fails on
    mixed-type keys (json's sort_keys cannot compare int and str). Documented
    consequence: an int key and its string form collide — do not mix them."""
    if isinstance(obj, dict):
        return {str(k): _stringify_keys(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_stringify_keys(x) for x in obj]
    return obj


def _canonical_json(obj: Any) -> str:
    """Deterministic JSON: stringified keys, sorted, no whitespace variance,
    non-JSON types via str()."""
    return json.dumps(_stringify_keys(obj), sort_keys=True, separators=(",", ":"), default=str)


def stable_id(payload: dict[str, Any], *, length: int = 12) -> str:
    """Content-derived pointer: sha256 of the canonical JSON, truncated.
    Same content → same id, across sessions and machines."""
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return digest[:length]


def _sort_token(v: Any) -> tuple[int, float, str]:
    """Type-aware, totally ordered token: numeric values (non-bool) compare
    numerically — 2.0 sorts before 10.0, -5 before -1 — everything else
    compares by canonical JSON string. Numbers sort before non-numbers when a
    key holds mixed types (deterministic and documented)."""
    if not isinstance(v, bool) and isinstance(v, (int, float)):
        return (0, float(v), "")
    return (1, 0.0, _canonical_json(v))


def canonical_sort(
    records: Iterable[dict[str, Any]],
    keys: Sequence[str],
) -> list[dict[str, Any]]:
    """THE canonical order for a record set: type-aware over ``keys`` (numeric
    keys compare numerically, not as strings), with ``stable_id`` of the full
    record as the final tie-breaker so the order is total and deterministic
    even for records identical on all sort keys.

    Raises on a record missing any sort key — silent partial ordering is how
    order-dependence sneaks back in.
    """
    records = list(records)
    for i, r in enumerate(records):
        missing = [k for k in keys if k not in r]
        if missing:
            raise KeyError(f"record {i} missing sort keys {missing}")

    def sort_key(r: dict[str, Any]):
        return tuple(_sort_token(r[k]) for k in keys) + (stable_id(r),)

    return sorted(records, key=sort_key)


def order_invariant_digest(records: Iterable[dict[str, Any]]) -> str:
    """Digest of a record set that is identical for ANY input permutation —
    the check that a read/aggregation path does not depend on presentation
    order: digest the multiset, not the sequence."""
    hashes = sorted(
        hashlib.sha256(_canonical_json(r).encode("utf-8")).hexdigest()
        for r in records
    )
    return hashlib.sha256("".join(hashes).encode("utf-8")).hexdigest()[:16]
