# Vendored axel-qt-unit-test-generate

C++ Qt Test generation skill vendored per the monorepo external-dependency
policy in `CLAUDE.md`.

Upstream: https://github.com/eric2023/qt-unit-test-generate
License: Apache-2.0 (see `LICENSE`)
Pinned ref: `ee11ff31f6f0b31b5a4ab8cb9c4cf9ee904b9c3e` (`main`, vendored 2026-08-22)

## Local Changes

Kept minimal so the vendored tree stays diffable against upstream:

1. Renamed frontmatter `name:` from `qt-unit-test-generate` to
   `axel-qt-unit-test-generate`.
2. Added pinned-source provenance keys and corrected the declared license from
   the README's incorrect `MIT` to the bundled `Apache-2.0`.
3. Translated the frontmatter description into English; retained upstream body
   content in its original language for easier upstream diffs.
4. Added Axel scope rules for `qt/`, generated-test promotion, dynamic libclang
   discovery, offscreen execution, the eight-job build cap, and disposable
   mutation build directories.
5. Corrected the README license statement to Apache-2.0.
6. Removed upstream `.gitignore` and `.git`; neither is skill content.

## Review Findings

- The five scripts compile with Python 3.12 syntax checking.
- Upstream has no executable test harness. Its `example/` results are claims,
  not reproducible validation in this repository.
- The skill assumes Linux and LLVM/libclang; treat it as a candidate generator,
  not a turnkey gate, until its example pipeline is exercised against Axel's Qt
  build.

## Updating

Refresh only from the pinned upstream repository, reapply the rename,
provenance, license correction, Axel scope, and cleanup changes, then update
this file and the provenance keys.
