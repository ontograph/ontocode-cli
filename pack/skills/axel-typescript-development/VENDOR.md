# Vendored TypeScript Development

Derived from an external agent skill, vendored per the monorepo external-dependency
policy in `CLAUDE.md`.

Upstream: https://github.com/sickn33/agentic-awesome-skills
Upstream path: `skills/typescript-expert`
License: MIT
Pinned ref: `b6ceca367a3b3ee90a273a3afa895960e8e9d7a5` (`main`, vendored 2026-08-22)
Catalog entry: https://skills.sh/sickn33/agentic-awesome-skills/typescript-expert

## Local Changes

Unlike `axel-rust-standard`, this is a full rewrite rather than a diffable copy: no
upstream text is retained verbatim, so the pinned ref records origin, not a merge base.
Renamed `typescript-expert` -> `axel-typescript-development`.

Removed deliberately:

- `scripts/ts_diagnostic.py` — ran shell strings with `shell=True`, invoked `npx` (network fetch), ignored subprocess exit codes, reported "No type errors" when the compiler was merely missing, and always exited 0. It also assumed a root `tsconfig.json`/`src/`, which does not match this repository.
- `references/tsconfig-strict.json`, `references/typescript-cheatsheet.md`, `references/utility-types.ts` — generic material unrelated to this repository's TypeScript 4.4.2 / `target: es5` / `module: none` build.
- Upstream routing to `typescript-build-expert`, `typescript-module-expert`, `typescript-type-expert`, none of which are installed.
- Tool recommendations (Biome, Nx/Turborepo, ts-migrate, Vitest) that conflict with this repository's toolchain.

## Updating

Do not copy upstream content back in. If upstream changes materially, re-derive the
guidance against this repository and update the pinned ref above.

## Install

The repository copy is authoritative. Run `scripts/sync-skills.sh` to refresh the
local discovery tree, then run `scripts/check-skill-wiring.sh`.
