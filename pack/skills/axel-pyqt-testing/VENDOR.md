# Vendored axel-pyqt-testing

PyQt/PySide6 testing skill vendored per the monorepo external-dependency policy
in `CLAUDE.md`.

Upstream: https://github.com/CodeAtCode/oss-ai-skills
License: GPL-3.0-only (see `LICENSE`)
Pinned ref: `30e045383bee16ac7c0c55702fdcc511ef57990c` (`main`, vendored 2026-08-22)
Upstream path: `frameworks/pyqt/testing`

## Local Changes

Kept minimal so the vendored skill stays diffable against upstream:

1. Renamed frontmatter `name:` from `pyqt-testing` to `axel-pyqt-testing`.
2. Added license and pinned-source provenance keys.
3. Added the upstream repository `LICENSE`; upstream shipped only the skill file.
4. Added Axel scope boundaries for Python tooling rather than the C++ `qt/`
   client, isolated dependencies, offscreen execution, committed regressions,
   and the repository build-job cap.
5. Normalized end-of-line whitespace to satisfy the repository whitespace gate.

## Updating

Refresh only from the pinned upstream path, reapply the rename, provenance,
license, and Axel scope changes, then update this file and the provenance keys.
