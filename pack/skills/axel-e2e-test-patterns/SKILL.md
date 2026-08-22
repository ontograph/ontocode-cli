---
name: axel-e2e-test-patterns
description: Playwright run hygiene for Axel - flaky-test quarantine, artifact management, CI wiring, and run reporting. Use when triaging flaky E2E runs or organizing run artifacts. For writing or restructuring specs, use axel-author-playwright-specs.
metadata:
  origin: ECC
---

# E2E Run Hygiene

Flaky-test handling, artifacts, CI, and reporting for the Axel Playwright suite.

Authoring rules -- locators, waiting, assertions, Page Object structure, and
config -- live in `$axel-author-playwright-specs`. This skill deliberately does
not restate them, because two authoring authorities drift and the losing copy
becomes a citation for the wrong pattern.

## Flaky Test Patterns

### Quarantine

```typescript
test('flaky: complex search', async ({ page }) => {
  test.fixme(true, 'Flaky - Issue #123')
  // test code...
})

test('conditional skip', async ({ page }) => {
  test.skip(process.env.CI, 'Flaky in CI - Issue #123')
  // test code...
})
```

### Identify Flakiness

```bash
npx playwright test tests/search.spec.ts --repeat-each=10
npx playwright test tests/search.spec.ts --retries=3
```

### Common Causes & Fixes

**Race conditions:**
```typescript
// Bad: assumes element is ready
await page.click('[data-testid="button"]')

// Good: auto-wait locator
await page.locator('[data-testid="button"]').click()
```

**Network timing:**
```typescript
// Bad: arbitrary timeout
await page.waitForTimeout(5000)

// Good: wait for specific condition
await page.waitForResponse(resp => resp.url().includes('/api/data'))
```

**Animation timing:**
```typescript
// Bad: click during animation
await page.click('[data-testid="menu-item"]')

// Good: wait for stability
// Actionability checks cover visible, stable, and enabled; no networkidle needed.
await expect(page.getByRole('menuitem', { name: 'Open' })).toBeVisible()
await page.getByRole('menuitem', { name: 'Open' }).click()
```

## Artifact Management

### Screenshots

```typescript
await page.screenshot({ path: 'artifacts/after-login.png' })
await page.screenshot({ path: 'artifacts/full-page.png', fullPage: true })
await page.locator('[data-testid="chart"]').screenshot({ path: 'artifacts/chart.png' })
```

### Traces

```typescript
await browser.startTracing(page, {
  path: 'artifacts/trace.json',
  screenshots: true,
  snapshots: true,
})
// ... test actions ...
await browser.stopTracing()
```

### Video

```typescript
// In playwright.config.ts
use: {
  video: 'retain-on-failure',
  videosPath: 'artifacts/videos/'
}
```

## CI/CD Integration

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
        env:
          BASE_URL: ${{ vars.STAGING_URL }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

## Test Report Template

```markdown
# E2E Test Report

**Date:** YYYY-MM-DD HH:MM
**Duration:** Xm Ys
**Status:** PASSING / FAILING

## Summary
- Total: X | Passed: Y (Z%) | Failed: A | Flaky: B | Skipped: C

## Failed Tests

### test-name
**File:** `tests/e2e/feature.spec.ts:45`
**Error:** Expected element to be visible
**Screenshot:** artifacts/failed.png
**Recommended Fix:** [description]

## Artifacts
- HTML Report: playwright-report/index.html
- Screenshots: artifacts/*.png
- Videos: artifacts/videos/*.webm
- Traces: artifacts/*.zip
```

## Axel Context

- Suite lives in `browser/playwright_tests/` (projects: e2e, ui-assurance, xl-perf); config is `browser/playwright_tests/playwright.config.ts`.
- Run through `browser/playwright_tests/ui-assurance/run-profile.py` profiles (`ui-smoke`, `ui-complete`) or the pwrunner sidecar (`runner-sidecar.mjs`); reporters are registered via env vars (`PWRUNNER_NDJSON_OUT`, `PLAYWRIGHT_JSON_OUTPUT_NAME`), CLI `--reporter` is ignored.
- Artifacts: `test-results/`, `playwright-report/`, `.pwrunner-runs/` inside `browser/playwright_tests/`.
- Known debt to avoid reintroducing: vacuous stub assertions in `lib/cool-page.ts`, `trace: 'off'` on the e2e project, ~175 `waitForTimeout` calls, hardcoded nvm path in ui-assurance specs.
- No user login flows here — the only auth is the sidecar bearer token in `fixtures.ts`; skip storageState/auth-setup patterns.

