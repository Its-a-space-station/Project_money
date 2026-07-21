# AGENTS.md — Project_money

This project's operating rules and research philosophy live in a single canonical
file: **[CLAUDE.md](CLAUDE.md)**. Codex (and any other coding agent) must read it
fully before acting — it is the source of truth for this repo.

The short version (see `CLAUDE.md` for the binding text):

- **Research-only.** This system does not buy, sell, trade, place orders, or move
  funds — ever, including from any loop or schedule.
- **Human-in-the-loop** for anything irreversible or outward-facing.
- **Verify before asserting** (maker ≠ checker); unverifiable items become tracked
  verification debt.
- **Canonical labels only** (see [docs/label_policy.md](docs/label_policy.md)); no
  action words as labels or field names.
- **No secrets in the repo.** Robinhood is **read-only, gated, and treated as a
  broker** — no execution path.
- **Explicit-path git only**; ask before staging or committing; never push without
  approval.

Do not duplicate the rules here — if guidance changes, change `CLAUDE.md`.
