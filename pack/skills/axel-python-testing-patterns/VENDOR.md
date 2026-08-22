# Vendored axel-python-testing-patterns

Python skill vendored per the monorepo external-dependency policy in
`CLAUDE.md`.

Upstream: https://github.com/wshobson/agents
License: MIT (see `LICENSE`)
Pinned ref: `367cb6a4a182cf7e9b0a17c9429f7411ddd9cf35` (`main`, vendored 2026-08-22)
Upstream path: `plugins/python-development/skills/python-testing-patterns`
Upstream version: main @ 367cb6a

## Local Changes

Kept minimal so the vendored skill stays diffable against upstream:

1. Renamed the `SKILL.md` frontmatter `name:` from `python-testing-patterns` to
   `axel-python-testing-patterns`.
2. Added `vendored_from`, `vendored_ref`, and `vendored_on` provenance keys.
3. Added the upstream repository `LICENSE` to this vendored directory.
4. Added Axel Workspace Overrides for Python 3.11+, repository-owned coverage and
   dependencies, production-code imports, environment isolation, strict markers,
   and meaningful coverage over a bare percentage target.
5. Fixed incomplete imports, host-environment leakage, a fake database-reset
   fixture, stale Python 3.9 CI, and test-module production-code examples.

## Updating

Refresh only from the pinned upstream path, reapply the renames above, and
reapply these local changes; update this file plus the `SKILL.md` provenance keys.
