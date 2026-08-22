# Vendored axel-python-pro

Python skill vendored per the monorepo external-dependency policy in
`CLAUDE.md`.

Upstream: https://github.com/Jeffallan/claude-skills
License: MIT (see `LICENSE`)
Pinned ref: `882ef55e377dbf9a4dbe496bb41ac6ccd0e555cf` (`main`, vendored 2026-08-22)
Upstream path: `skills/python-pro`
Upstream version: 1.1.0

## Local Changes

Kept minimal so the vendored skill stays diffable against upstream:

1. Renamed the `SKILL.md` frontmatter `name:` from `python-pro` to
   `axel-python-pro`.
2. Added `vendored_from`, `vendored_ref`, and `vendored_on` provenance keys.
3. Added the upstream repository `LICENSE` to this vendored directory.
4. Added an Axel Workspace Overrides section for Python 3.11+, Ruff-only
   formatting, repository-owned coverage/dependency policy, and bounded async I/O.
5. Replaced unsafe/unbounded gather examples with structured TaskGroup examples,
   fixed their result/error handling, and removed Black from packaging guidance.

## Updating

Refresh only from the pinned upstream path, reapply the renames above, and
reapply these local changes; update this file plus the `SKILL.md` provenance keys.
