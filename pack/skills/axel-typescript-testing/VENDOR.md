# Vendored TypeScript Testing

Derived from an external agent skill, vendored per the monorepo external-dependency
policy in `CLAUDE.md`.

Upstream: https://github.com/github/awesome-copilot
Upstream path: `skills/javascript-typescript-jest`
License: MIT
Pinned ref: `83561bd7d8a46fcda0581aedabdf8eac7cb196b6` (`main`, vendored 2026-08-22)
Catalog entry: https://skills.sh/github/awesome-copilot/javascript-typescript-jest

## Local Changes

This is a replacement, not a diffable copy. Only the general idea of documented test
discipline was kept; the pinned ref records origin, not a merge base.
Renamed `javascript-typescript-jest` -> `axel-typescript-testing`.

Removed deliberately:

- All Jest specifics (`jest.mock`, `jest.spyOn`, `jest.resetAllMocks`, `jest.setTimeout`, snapshot testing, Jest matcher list). This repository runs Mocha 8.2.1, Playwright, and WebdriverIO. Jest is not a dependency.
- React Testing Library and `userEvent` guidance; there is no React test surface here.
- The blanket "reset all mocks in afterEach" rule, replaced by matching the surrounding suite's teardown style.

## Updating

Upstream is Jest-specific and does not apply to this repository. Do not re-import.

## Install

The repository copy is authoritative. Run `scripts/sync-skills.sh` to refresh the
local discovery tree, then run `scripts/check-skill-wiring.sh`.
