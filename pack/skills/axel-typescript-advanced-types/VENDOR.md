# Vendored Advanced TypeScript Types

Derived from an external agent skill, vendored per the monorepo external-dependency
policy in `CLAUDE.md`.

Upstream: https://github.com/wshobson/agents
Upstream path: `plugins/javascript-typescript/skills/typescript-advanced-types`
License: MIT
Pinned ref: `367cb6a4a182cf7e9b0a17c9429f7411ddd9cf35` (`main`, vendored 2026-08-22)
Catalog entry: https://skills.sh/wshobson/agents/typescript-advanced-types

## Local Changes

This rewrite inverts the upstream intent: upstream teaches advanced type techniques
broadly, this skill constrains their use to cases simpler types cannot express. No
upstream text is retained verbatim, so the pinned ref records origin, not a merge base.
Renamed `typescript-advanced-types` -> `axel-typescript-advanced-types`.

Removed deliberately:

- `references/details.md` — worked examples with defects, including an API-client type requiring every endpoint to satisfy every HTTP method, and a builder whose default state conflicts with its own mapped-type constraint. Several examples also used `any`/`as any` while the prose advised against it.
- Encouragement of branded types, `Deep*` utility families, and reusable type-library construction for single callers.

## Updating

Do not copy upstream examples back in. Any pattern must be proven against real Axel
call sites first.

## Install

The repository copy is authoritative. Run `scripts/sync-skills.sh` to refresh the
local discovery tree, then run `scripts/check-skill-wiring.sh`.
