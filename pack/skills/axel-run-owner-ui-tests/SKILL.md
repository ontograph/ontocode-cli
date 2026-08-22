---
name: axel-run-owner-ui-tests
description: Run Axel L0-L2 UI/UX checks at the layer that owns the behavior. Use for source gates, browser Mocha, browser-owned Playwright chrome, Rust, C++, LibreOffice CppUnit, and focused coverage without claiming native-grid behavior.
---
# Run Axel Owner-Layer UI Tests

Read `.memory-bank/ui-ux-assurance/TEST-ARCHITECTURE.md` and the relevant verification matrix before selecting commands. Preserve the dirty worktree and do not default to a clean rebuild.

For a named assurance profile or matrix row, confirm `scripts/uiux/assurance.py` exists and preflight the existing contract before execution:

```bash
python3 scripts/uiux/assurance.py preflight --profile ui-smoke
python3 scripts/uiux/assurance.py preflight --profile ui-smoke --matrix-id CI-SEL-001
```

`preflight` checks prerequisites without running tests. Exit `0` is `READY`, `1` is a failed runnable prerequisite, and `2` is `HOLD` because no selected row is runnable. Continue profile execution through `scripts/run-ui-assurance.sh`; do not turn the CLI into another runner.

## Execute narrowly

1. Record HEAD, changed files, build identity, platform, and the claim under test.
2. Run applicable L0 gates first, normally `scripts/select-gates.sh --run` and `./scripts/verify-changed-no-binaries.sh`; add architecture-specific checks only when relevant.
3. Run one narrow L1 owner test:
   - Browser policy/logic: `cd browser && npm run build-tests && npm test`, or the documented focused npm target.
   - Rust/C++/LOKit: use the exact focused command named by current source or the architecture document.
   - Required focused coverage: `scripts/run-focused-coverage.sh --required`.
4. Add L2 only for a component or browser-owned route/chrome boundary:
   `cd browser/playwright_tests && npx playwright test e2e/<uc-id>/<spec>.spec.ts`.
   When authoring or modifying an L2 spec, follow `$axel-author-playwright-specs` for locator, waiting, and assertion rules; create a spec for an uncovered route through `$axel-generate-playwright-specs`. Before a new or edited spec backs a matrix row, pass `scripts/check-e2e-spec-smells.sh` and a `$axel-review-e2e-specs` audit; a spec that cannot fail proves nothing.
5. For a requested profile, run the authoritative coordinator, for example `scripts/run-ui-assurance.sh --profile ui-smoke`, after a successful preflight.
6. Preserve exact command, exit code, expected versus actual assertions, relevant log excerpts, and artifact paths.

When a retained baseline exists, compare it with current supported evidence after independently verifying both packets:

```bash
python3 scripts/uiux/assurance.py compare <baseline> <current> --output <comparison.json>
```

Exit `0` means comparable with no detected regression, `1` means a valid comparable regression, and `2` means incomplete or incomparable provenance. Do not use `compare` to make native-grid claims from browser evidence.

Before treating an intermittent L2 failure as a regression, check whether the test already had instability:

```bash
python3 scripts/uiux/assurance.py flake-history browser/playwright_tests/.pwrunner-runs
```

That ledger only has data if runs were retained. Set `PWRUNNER_NDJSON_OUT` to a path under `build-scratch/evidence/pwrunner-runs/` when running a profile locally; CI retains it as a ui-smoke artifact.

## Live browser session

`e2e/` specs skip unless `COOL_E2E_SERVER` is set. To run them for real:

```bash
cp test/data/empty.ods /tmp/fixture.ods
scripts/run-e2e-cool-server.sh --port 9980     # prints READY ... pid=<PID>
cd browser/playwright_tests && npm ci
COOL_E2E_SERVER='http://localhost:9980/browser/dist/cool.html?file_path=/tmp/fixture.ods' \
  npx playwright test --project=e2e e2e/<uc-id>/<spec>.spec.ts --reporter=line
kill -INT <PID>
```

Prove the bundle is current before believing any result. `build-scratch/browser/dist` can be weeks older than `browser/src`, in which case the run exercises history, not your change; the launcher warns when it detects this. `coolwsd` serves the bundle under a hashed path and caches it per process, so a rebuilt bundle needs a server restart before the new code is served.

A bare `npx playwright test` does not emit sidecar NDJSON, so it produces no `flake-history` evidence. Use the profile runner when the run is meant to be retained.

## Browser boundary

Playwright may prove menus, dialogs, formula/address/status bars, preferences, and other browser-owned chrome. It must not prove native-grid rendering, input, focus, selection, geometry, or repaint. Route those claims to `$axel-run-qt-ui-scenarios`.

A red L2 result is analysed from its Playwright report artifacts by `$axel-debug-playwright-reports` before escalating; escalate to `$axel-debug-uiux-tests` when the first divergent boundary is native, cross-surface, or environmental rather than browser-owned.

The same boundary binds raw Chrome DevTools Protocol access. `run-qt.sh` exposes CDP on
`:59222` under `CODA_QT_REMOTE_DEBUG=1`, and the `chrome-devtools-axel` MCP server or
`$faster-chrome-devtools-skill` may attach to it. CDP reaches the Qt WebEngine renderer
DOM, JS, console, and network only. Protocol proximity does not raise evidence level:
a CDP snapshot, screenshot, or evaluated expression is L2 browser-owned evidence and
never proves native-grid pixels, real input, focus, selection, geometry, or visible repaint.
Use `CODA_QT_DEBUG=1` only as a short probe; it forces `QT_LOGGING_RULES="*=true"` and
invalidates performance measurement.

## Verdict

- `PASS`: every scoped runnable check passes and provenance is complete.
- `FAIL`: an owned assertion, gate, crash, or required runnable test fails.
- `HOLD`: a required environment or artifact is unavailable.

Do not rerun until green and hide earlier attempts. Record every attempt. Stop downstream layers when startup or composition prerequisites fail.

