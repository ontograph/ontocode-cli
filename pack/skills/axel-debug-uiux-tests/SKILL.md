---
name: axel-debug-uiux-tests
description: Diagnose Axel UI/UX test failures at the first divergent boundary. Use for crashes, startup, rendering, focus/input, browser-native synchronization, persistence, performance, flaky scenarios, and environment blocks.
---
# Debug Axel UI/UX Tests

Diagnose only unless the user explicitly requests repair. Read `TEST_DEBUG_LOOP_GUIDE.md`, `UI_UX_TEST_PATTERNS.md`, and current `.memory-bank/ui-ux-assurance/TEST-ARCHITECTURE.md`; current architecture overrides historical example commands.

When the failure has a profile summary, cell-interaction bundle, or visual manifest, confirm `scripts/uiux/assurance.py` exists and begin with:

```bash
python3 scripts/uiux/assurance.py triage <evidence>
python3 scripts/uiux/assurance.py triage <profile-summary> --matrix-id <matrix-id>
```

Use its boundary, category, matrix row, owner, reason, action index, and next command to seed the narrow reproduction. Exit `0` means no divergent boundary was found, `1` reports a failure boundary, and `2` is a capability/provenance `HOLD`. Triage identifies the first contract-visible divergence; it does not prove root cause or authorize repair.

For a browser-owned (Playwright) row, `next_command` names the Playwright artifact reader against the row's report directory instead of a rerun. Hand that analysis to `$axel-debug-playwright-reports`, which owns report, trace, and flake classification; keep native-grid, cross-surface, startup, persistence, and environment boundaries in this skill. The e2e project currently runs `trace: 'off'`, so expect no trace for e2e rows until that config is fixed.

If a known-good baseline and current supported evidence packet both exist, run:

```bash
python3 scripts/uiux/assurance.py compare <baseline> <current> --output <comparison.json>
```

Use `FAIL` to identify a result regression, new issue, or numeric budget increase. Treat exit `2/HOLD` as a provenance or comparability failure and repair the evidence packet before diagnosing product behavior. `compare` does not replace first-boundary triage.

## Reproduce and classify

1. Preserve first-failure evidence before cleanup or restart: exact command/exit, HEAD/binary/fixture, environment, ordered actions, logs, screenshots/recordings, and state records.
2. Build the smallest red-capable reproduction through the owning layer. Do not replace a native failure with a browser DOM probe.
3. Identify the first divergent boundary:
   - environment/tooling;
   - startup/initialization;
   - composition/rendering;
   - interaction/input/focus/state;
   - backend/synchronization;
   - persistence/integration;
   - crash/memory safety;
   - performance/stability.
4. Form ranked falsifiable hypotheses and add only the instrumentation needed to distinguish them.
5. Reproduce once more explicitly when required by promotion rules. Record both attempts; never rerun until green and report only the last result.

## Instrument carefully

- Use targeted Qt/WebEngine logging first. Full `*=true` logging is a short probe and invalidates performance measurements.
- Use `QT_DEBUG_PLUGINS=1` only for plugin/startup suspicions.
- For a live renderer probe, start the app with `CODA_QT_REMOTE_DEBUG=1 ./run-qt.sh` and attach over CDP on `:59222` via the `chrome-devtools-axel` MCP server or `$faster-chrome-devtools-skill`. Prefer this over `CODA_QT_DEBUG=1`, which opens the same port but also forces `QT_LOGGING_RULES="*=true"`.
- CDP evidence stays L2 browser-owned: renderer DOM, JS, console, and network. It never proves native-grid pixels, real input, focus, selection, geometry, or visible repaint, and does not replace first-boundary triage.
- Preserve the exact binary and arguments for GDB. ASAN claims require an ASAN-instrumented build; Valgrind and `perf` require availability, permissions, and representative execution.
- Track and gracefully terminate only the recorded PID. Never use broad `pkill -9` cleanup.
- When the first divergent boundary is crash/memory safety, hand off to `$axel-triage-native-crash`, which owns core-dump and sanitizer analysis via `scripts/uiux/crash-triage.sh`.
- Do not treat `time --help`, raw `ENOENT` counts, brittle pixel hashes, or a screenshot alone as acceptance evidence.

## Stop conditions

Stop with `HOLD` when the exact symptom cannot be reproduced because the required host, display, tool, fixture, or trace is unavailable. Stop before production repair and report the first divergent state, owning layer, evidence, likely next narrow regression, and bounded repair handoff. If repair is later authorized, closure requires both the narrow reproduction and original end-to-end scenario to pass.

