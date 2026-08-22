# Vendored axel-python-performance-optimization

Python skill vendored per the monorepo external-dependency policy in
`CLAUDE.md`.

Upstream: https://github.com/wshobson/agents
License: MIT (see `LICENSE`)
Pinned ref: `367cb6a4a182cf7e9b0a17c9429f7411ddd9cf35` (`main`, vendored 2026-08-22)
Upstream path: `plugins/python-development/skills/python-performance-optimization`
Upstream version: main @ 367cb6a

## Local Changes

Kept minimal so the vendored skill stays diffable against upstream:

1. Renamed the `SKILL.md` frontmatter `name:` from `python-performance-optimization` to
   `axel-python-performance-optimization`.
2. Added `vendored_from`, `vendored_ref`, and `vendored_on` provenance keys.
3. Added the upstream repository `LICENSE` to this vendored directory.
4. Added Axel Workspace Overrides requiring profiling before optimization,
   monotonic benchmark timing, bounded caches, shallow-size caveats, and explicit
   dependency/build approval before NumPy or native extensions.
5. Corrected timing and memory-comparison snippets in `references/`.

## Updating

Refresh only from the pinned upstream path, reapply the renames above, and
reapply these local changes; update this file plus the `SKILL.md` provenance keys.
