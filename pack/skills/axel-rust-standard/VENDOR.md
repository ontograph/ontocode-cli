# Vendored Rust Standard

Base Rust coding standard for the `rust/` workspace, vendored per the monorepo
external-dependency policy in `CLAUDE.md`.

Upstream: https://github.com/leonardomso/rust-skills
License: MIT (see `LICENSE`) - Copyright (c) 2025 Leonardo Maldonado
Pinned ref: `fd2a861ab0406a4ac536a55274d14ea6fd1ca9c9` (`master`, vendored 2026-08-22)
Upstream version: 1.5.1 (265 rules, 26 categories)

## Local Changes

Kept minimal so the vendored tree stays diffable against upstream:

1. `SKILL.md` frontmatter `name:` renamed `rust-skills` -> `axel-rust-standard`,
   invocation renamed `/rust-skills` -> `/axel-rust-standard`, and `vendored_*`
   provenance keys added.
2. `SKILL.md` gained an "Axel Workspace Overrides" section pointing at
   `axel-rust-supplement` for edition/MSRV and measure-first precedence.
3. Removed upstream `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md`. The first two
   are agent-instruction files that would be misread as belonging to this repo;
   the third describes contributing to the upstream project.
4. Removed `checks/`, the upstream dev harness that compile-verifies rule examples.
   It carries its own `Cargo.toml`, `Cargo.lock`, and `rust-toolchain.toml`, which
   would collide with the `rust/` workspace and pin an unrelated toolchain.
5. Removed upstream `README.md`: install instructions (`npx add-skill ...`) and
   `/rust-skills` invocations that do not apply to a vendored copy. `CHANGELOG.md`
   is kept because it helps review upstream diffs.
6. Removed upstream `.github/workflows/ci.yml`. It drives the deleted `checks/`
   harness and would otherwise register as a workflow of this repository.

The 265 files under `rules/` are unmodified upstream text.

## Companion Skill

`.claude/skills/axel-rust-supplement/` covers what this standard omits: C ABI/FFI
boundary discipline, `Pin`, panic strategy, and supply-chain gates. It also defines
the precedence rules that override parts of this vendored text. Load both.

## Updating

```bash
# Review upstream changes before pulling them in.
gh api repos/leonardomso/rust-skills/compare/fd2a861ab0406a4ac536a55274d14ea6fd1ca9c9...master \
  --jq '.files[].filename'
```

Re-apply the local changes above after any refresh, and update the pinned ref and
date in this file and in the `SKILL.md` frontmatter.
