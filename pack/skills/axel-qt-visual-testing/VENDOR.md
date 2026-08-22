# Vendored axel-qt-visual-testing

Offscreen Qt screenshot skill vendored per the monorepo external-dependency
policy in `CLAUDE.md`.

Upstream: https://github.com/talmolab/sleap
License: BSD-3-Clause-Clear (see `LICENSE`)
Pinned ref: `6967e049debfe9a14818c5708c6c0dca1743e698` (`main`, vendored 2026-08-22)
Upstream path: `.claude/skills/qt-testing`

The closely related `toonoumi/FreeCCR` derivative was reviewed and not vendored:
it is application-specific, AGPL-3.0 licensed, and computes paths from its
original four-level repository layout. Its useful explicit-offscreen behavior is
covered by this copy's Axel override instead.

## Local Changes

Kept minimal so the vendored skill stays diffable against upstream:

1. Renamed frontmatter `name:` from `qt-testing` to `axel-qt-visual-testing`.
2. Added license and pinned-source provenance keys.
3. Added the upstream repository `LICENSE`.
4. Added Axel scope limits separating exploratory Python screenshots from
   committed C++ `qt/` tests and evidence storage rules.
5. Changed default output from `scratch/.qt-screenshots` to
   `AXEL_QT_SCREENSHOT_DIR` or `build-scratch/evidence/qt-visual`.
6. Defaulted newly created Qt applications to the offscreen platform.

## Updating

Refresh only from the pinned upstream path, reapply the rename, provenance,
license, Axel scope, output-path, and offscreen changes, then update this file
and the provenance keys.
