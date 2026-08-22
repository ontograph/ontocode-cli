---
name: axel-run-qt-ui-scenarios
description: Run Axel L3 native-grid and cross-surface Qt UI scenarios. Use for real selection, editing, keyboard, focus, repaint, browser-native synchronization, and desktop lifecycle through Qt WDIO, AT-SPI, and physical input.
---
# Run Axel Qt UI Scenarios

Use `.memory-bank/ui-ux-assurance/TEST-ARCHITECTURE.md`, the accepted scenario-driven Qt ADR, and the matching tracker matrix as authority. Work through existing `qt/test/` runners and `qt/test/scenarios/`; do not add a framework or browser-grid substitute.

## Preflight

1. Name the scenario or matrix row and its expected transitions.
2. For a profile or matrix row, confirm `scripts/uiux/assurance.py` exists and run `python3 scripts/uiux/assurance.py preflight --profile ui-smoke --matrix-id <matrix-id>`. This checks the manifest, command, fixture, binary, driver, and runtime prerequisites without executing the scenario.
3. Interpret exit `0` as `READY`, `1` as a failed runnable prerequisite, and `2` as `HOLD`; do not start the scenario unless preflight is `READY`.
4. Record HEAD, binary and asset identity, copied fixture hash/format, locale, theme, scale/DPR, QPA/display/session, input method, accessibility driver, and artifact directory.
5. Copy every mutable fixture. Use an isolated application process and retain its exact PID.
6. If required physical input, Wayland, IME, touchpad, Orca, scale, or theme is unavailable, return `HOLD`.

## Execute

For bounded exploratory coverage, generate the action plan before launching Qt:

```bash
python3 scripts/uiux/assurance.py explore \
  --seed <integer> --length <count> --fixture <copied-fixture> \
  --output <plan.json>
```

The planner is deterministic and never runs Qt. It returns `2/HOLD` until the scenario runner supplies a JSON list of `length + 1` observed states containing `address`, `selection`, `bounds`, and `focus_owner`. Re-run with `--observed-states <states.json>` to bind the observed sequence into a `PASS` plan. Execute actions through the existing declarative Qt harness; do not add another runner.

Run the narrow focused spec before broader profiles. Typical current forms are:

```bash
cd qt/test
AT_SPI_DRIVER_PATH=/path/to/selenium-webdriver-at-spi.py \
  ./run-tests.sh --spec ./specs/cell-input.spec.ts
```

```bash
cd qt/test
CODA_QT_TEST_SCENARIO=editing-enter \
AT_SPI_DRIVER_PATH=/path/to/selenium-webdriver-at-spi.py \
  ./run-tests.sh --spec ./specs/cell-scenarios.spec.ts
```

Use `scripts/run-ui-assurance.sh --profile ui-smoke` before `ui-complete` when matrix-wide profile execution is requested. Automatic retries are zero. A reproduction is an explicit second run with both outcomes retained.

The assurance CLI inspects existing contracts and evidence; it never replaces `scripts/run-ui-assurance.sh`, `qt/test/run-tests.sh`, or the focused Qt scenario runner.

For a physical platform matrix row, retain the verified scenario evidence and hand it to `$axel-qualify-ui-evidence` for `platform-packet capture`. Synthetic or emulated input remains diagnostic and cannot establish a physical PASS.

## Assert every transition

- Browser and native addresses agree.
- Selection is non-empty and in the active window.
- Exactly one focus owner exists; an expected focused dialog is visible.
- Native evidence reports `surface=QWidget`; browser-grid DOM is absent and retired.
- Destructive actions produce an authoritative revision or pixel outcome.
- Logs show no crash, fallback, blank/red grid, `Unspecified Application Error`, or dirty close.

Fail immediately on any invariant violation. Screenshots support visual claims but never replace semantic state. Save/reopen claims continue through `$axel-verify-ui-persistence`.

## Evidence

Return exact commands/exits, scenario/action/state records, launcher logs, AT-SPI state and bounds, browser chrome state where relevant, native crops/screenshots, fixture/runtime hashes, clean-release proof, and `PASS`, `FAIL`, or `HOLD`.

