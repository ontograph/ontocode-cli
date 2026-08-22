---
name: axel-browser-client
description: Use when changing or reviewing the Axel/Collabora browser client under browser/src, browser/js, browser/css, or browser/mocha_tests, especially for legacy TypeScript 4.4, jQuery, CodeMirror, canvas, WebSocket, Mocha/jsdom, accessibility, or localization behavior.
license: MPL-2.0
metadata:
  owner: axel
  version: "1.0.0"
  scope: owned browser client, not vendored libraries or Playwright-only workflows
---

# Axel Browser Client

## Scope And Stack

- Owned code lives in `browser/src`, `browser/js`, `browser/css`, and
  `browser/mocha_tests`. Do not apply React, Vite, ESM bundler, or modern
  framework assumptions.
- The shipped client is an integrated jQuery/Leaflet-style application with
  CodeMirror 6, DOMPurify, Hammer.js, Apache Arrow, fzstd, and legacy
  Browserify/Uglify tooling. See `browser/package.json`.
- `browser/src` uses TypeScript 4.4 through the Autotools build. Mocha tests are
  separately compiled at ES2020 and do not imply that strict-mode-only syntax is
  valid in shipped source.
- Preserve the existing module style in the touched file. Check nearby callers
  before extracting a helper.

## Workflow

1. Read the nearest `tsconfig.json`, owning component, CSS contract, and focused
   tests before editing.
2. For interactive behavior, establish readiness first: load the owning surface,
   wait for its application state rather than a fixed sleep, then inspect the
   rendered DOM, console, network activity, canvas, or WebSocket messages.
3. Keep the diff at the product boundary: one behavior, its callers, and its
   observable state.
4. For HTML insertion, untrusted markup, timers, events, and cleanup, follow the
   established client patterns rather than introducing a parallel utility.
5. Test what the user can observe: visible result, enabled/disabled control,
   announced state, persisted document state, locale-specific text, or error
   surface. Do not assert implementation-private selectors when behavior is the
   contract.
6. Add or update one focused Mocha test for non-trivial logic.
7. Route HTTP/route end-to-end work and visual browser verification to the
   Playwright skills instead of expanding this skill.

## Validation

```sh
cd browser && npm ci && npm run build-tests && npm test
```

Run one behavior with:

```sh
cd browser && npm run test-single -- <pattern>
```

For shipped-source type/style changes, also use the configured targets:

```sh
cd browser && make eslint prettier
```

Report only the commands actually run. A compiled Mocha bundle is not proof that
the stricter shipped-client TypeScript build passed.

## Routing

- Language and package conventions: `$axel-typescript-development`
- Test design: `$axel-typescript-testing`
- End-to-end specs: `$axel-generate-playwright-specs`
- Visual/browser evidence: `$axel-verify-browser-ui`

## Routine Tool Ownership

This skill owns routine-tool operation 36, `BROWSER_UI_EVIDENCE_CAPTURE`, in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Capture
navigation, assertion, snapshot, screenshot, console, and network evidence as one
typed result using the coordinator's shared envelope.
