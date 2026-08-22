---
name: axel-typescript-testing
description: Choose the owning test layer and write TypeScript tests for Axel using its real Mocha, Playwright, and WebdriverIO stacks. Use for picking the right suite, writing or reviewing test code, async assertions, mocks, regression coverage, and running focused validation; do not introduce Jest or Vitest conventions.
---

# Axel TypeScript Testing

Choose the layer that owns the behavior. Axel does not use Jest for its browser unit suite.

## Select the test layer

- `browser/mocha_tests/` for browser-side units and source-adjacent behavior, compiled by the `build-tests` script in `browser/package.json`.
- `browser/playwright_tests/` for rendered UI, keyboard, focus, persistence, WebSocket, and cross-surface behavior.
- `qt/test/` (WebdriverIO, `wdio run wdio.conf.ts`) for the native Qt client harness.
- Reuse the nearest suite, fixture, helper, and assertion style. Do not create a new harness for one regression.
- Remember that these are separate packages and compile contracts: Mocha uses the browser TypeScript 4.4.2 binary through a non-strict ES2020 CLI build; Playwright has its own package; Qt WebdriverIO uses TypeScript 5.x with ESM.

## Test rules

- Reproduce the failure at the first divergent boundary before changing production code. For a regression, capture the focused failing run before the production fix and the passing run after it; do not claim red/green from inspection alone.
- Name the observed behavior and expected result; avoid implementation-only assertions.
- Await asynchronous operations and assertions. Never use arbitrary sleeps to make timing pass.
- Mock only external or nondeterministic boundaries. Prefer the real local collaborator when it is cheap and deterministic. Reuse existing fixtures and server/session lifecycle hooks rather than inventing another startup path.
- Reset state you mutated, in the teardown style the surrounding suite already uses.
- Keep regression coverage focused: one test that fails before the fix and passes after it, unless distinct branches matter.
- Do not add Jest globals, `jest.mock`, snapshots, React Testing Library, Vitest, or a new dependency to this repository.

## Validate

- Gates first: `scripts/select-gates.sh` lists what your change set selects; `scripts/select-gates.sh --run` executes them. Playwright spec edits select `scripts/check-e2e-spec-smells.sh` automatically.
- Mocha: `cd browser && npm run build-tests && npm run test-single -- <pattern>`. Full suite only when proportionate: `npm test`.
- Playwright: `browser/playwright_tests/node_modules` may be absent in a fresh checkout. Use `cd browser && npm run test:playwright`, which installs before running. Do not run a bare `npx playwright test` from an uninstalled package; report the gap instead of fetching ad hoc.
- Qt WebdriverIO: `cd qt/test && npm test`.
- Record the exact suite, spec, outcome, and any required environment or server setup. A focused pass is not a full-suite pass.

## Routing

- Use `$axel-typescript-development` for the implementation change itself.
- For Playwright specifics, hand off: `$axel-generate-playwright-specs` or `$axel-author-playwright-specs` to author, `$axel-review-e2e-specs` to review, `$axel-debug-playwright-reports` to triage failures, `$axel-e2e-test-patterns` for run hygiene and flake quarantine.
- For UI/UX packet selection and evidence, use `$axel-select-uiux-tests` and `$axel-qualify-ui-evidence`.
