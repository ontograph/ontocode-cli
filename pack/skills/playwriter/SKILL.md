---
name: playwriter
description: Validate browser UI behavior and capture screenshots through a host-installed Playwriter CLI. Use after frontend changes, when reproducing browser-only failures, or when DOM, console, network, navigation, or visual evidence is required.
---

# Playwriter

## Preflight

1. Run `command -v playwriter`.
2. If unavailable, report `blocked: playwriter CLI unavailable` and the host installation
   requirement. Do not install it, invoke a package manager, or download a browser.
3. Run `playwriter skill` and follow its current CLI/API contract. Repository and system
   instructions remain authoritative if they conflict with that output.

## Browser Session

Use a Playwriter-managed headless browser so the user's normal browser session is unaffected:

```bash
playwriter browser start --headless --user-data-dir "${TMPDIR:-/tmp}/ontocode-playwriter-profile"
playwriter session new
```

Keep the returned session ID and pass it with `-s` to subsequent commands. Use a dedicated
`state.page` for the task:

```bash
playwriter -s <session-id> -e 'state.page = await context.newPage(); await state.page.goto("<url>", { waitUntil: "domcontentloaded" })'
```

Use the user's real browser profile only when they explicitly request it or when authentication,
client certificates, or CAPTCHA make an isolated session invalid.

## Validation Loop

1. Observe before acting: inspect the URL, `snapshot({ page: state.page })`, and
   `getLatestLogs({ page: state.page, sinceLastCall: true })`.
2. Perform one meaningful interaction at a time using visible controls and stable selectors.
3. Observe again after each click, submit, form edit, or route change.
4. Use DOM snapshots for text and control assertions. Use screenshots for layout, rendering, and
   spatial evidence, always with absolute artifact paths.
5. Check relevant console and network evidence before declaring the workflow valid.
6. Remove task listeners with `state.page.removeAllListeners()` when listeners were attached.

Do not bypass UI behavior with `force: true`, synthetic `dispatchEvent`, or `element.click()` in
`page.evaluate()`. Prefer explicit selectors and load-state waits over sleeps. Do not close a shared
browser or context unless the user explicitly asks.

Completion requires evidence for the requested workflow at the required viewport, no relevant
unexpected browser errors, and artifact paths for any requested screenshots.
