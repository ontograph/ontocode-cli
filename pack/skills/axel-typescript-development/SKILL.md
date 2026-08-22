---
name: axel-typescript-development
description: Develop, refactor, and review TypeScript or JavaScript in the Axel client while preserving each owning package's TypeScript, ESLint, Prettier, and build conventions. Use for implementation changes under browser/src, browser/js, browser/tools, or qt/test that need project-specific typing, compiler compatibility, or gate selection guidance.
---

# Axel TypeScript Development

Work from the repository configuration and surrounding code. Do not import generic modern-TypeScript defaults into this older, integrated browser build.

## Ground rules

- Read `browser/package.json`, the nearest `tsconfig.json`, and surrounding files before editing.
- Use the compiler contract of the owning scope; do not carry one scope's settings into another.
- `browser/src` and `browser/js`: browser/package.json pins TypeScript 4.4.2. `browser/tsconfig.json` sets `strict: true`, `target: es5`, and `module: none`; do not assume bundler or ESM semantics.
- `browser/mocha_tests`: compiled by `npm run build-tests`, which invokes the TS 4.4.2 compiler with `--target ES2020` and does not enable full strict mode. Match the surrounding tests instead of importing strict-mode-only patterns.
- `qt/test`: uses TypeScript 5.x with ESM and WebdriverIO. Do not reject valid modern syntax merely because shipped browser code targets ES5.
- Match tabs, imports, naming, and module style in the touched file. Use `browser/.eslintrc` and `browser/.prettierrc` as authorities.
- Prefer existing types and helpers. Add the smallest type that closes the real boundary.
- Use `unknown` plus narrowing at trust boundaries. Do not replace sound existing code merely to eliminate every `any` or assertion.
- Do not add dependencies, change compiler flags, or migrate ESLint, Prettier, Mocha, or the module system without an explicit task and measured need.
- Fix a shared root cause once after checking callers. Avoid speculative generic utilities and type-level frameworks.
- In `browser/src`, use `safeSetHtml()` rather than assigning `innerHTML`, use `app.timerRegistry` rather than raw `setInterval`, and pair every added event listener with removal using the same handler reference or an explicit `{ once: true }`.

## Where TypeScript lives

- `browser/src` is the client source. `browser/tsconfig.json` excludes `mocha_tests` and `playwright_tests`; each has its own config.
- Shipped browser code compiles through `browser/Makefile.am` (`tscompile.done` and per-file `tsc` rules), not an npm build script. `npm run build-tests` only produces the Mocha bundle.
- `qt/test/lib/*.ts` is the WebdriverIO harness for the Qt client, run with `cd qt/test && npm test`.

## Workflow

1. Locate the owning package, `tsconfig.json`, call sites, and focused tests.
2. Classify the change as browser source, Mocha unit test, Playwright spec, or Qt WebdriverIO harness.
3. Implement the minimum compatible change.
4. Add or update one focused test for non-trivial behavior.
5. Let the repository choose the gates. Run `scripts/select-gates.sh` to list the gates your change set selects, then `scripts/select-gates.sh --run` to execute them in order, failing on the first error. Use `--staged` for staged changes. Do not hand-assemble a gate list.
6. Add the focused behavioral run the gates do not cover: `cd browser && npm run build-tests && npm run test-single -- <pattern>`.
7. For `browser/src` or `browser/js`, prove style separately when gates do not cover it: `cd browser && make eslint prettier`. Prove a shipped-source type change through the configured build tree so `tscompile.done` runs; a Mocha test pass alone does not prove strict browser compilation.
8. Report exact commands and results. Do not claim broader coverage than was run.

## Routing

- Use `$axel-typescript-testing` when the task is primarily test design, test selection, or test review.
- Use `$axel-typescript-advanced-types` only when ordinary interfaces, unions, narrowing, and built-in utility types cannot express the invariant clearly.
- Hand off Playwright work: `$axel-generate-playwright-specs` or `$axel-author-playwright-specs` to write specs, `$axel-debug-playwright-reports` to diagnose failures, `$axel-select-uiux-tests` to pick the owning packet.
