---
name: axel-triage-native-crash
description: Triage Axel native crashes from core dumps and sanitizer reports. Use for Qt/LOKit segfaults, aborts, ASAN/UBSAN findings, and any scenario whose first divergent boundary is crash/memory safety.
---
# Triage Axel Native Crashes

Diagnose only unless repair is explicitly requested. This skill owns the crash/memory-safety boundary that `$axel-debug-uiux-tests` identifies but does not analyse. Playwright report and trace analysis belongs to `$axel-debug-playwright-reports`; native process death belongs here.

## Preserve the crash first

A crash you cannot reproduce is evidence you already destroyed. Before restart or cleanup, record the exact binary path, arguments, environment, fixture hash, HEAD, and the recorded PID. Never use broad `pkill`.

Core dumps are off by default in most shells. Capture setup:

```bash
scripts/uiux/crash-triage.sh --enable-core-dumps
```

Run the scenario from a shell with `ulimit -c unlimited` so the kernel writes a core where `/proc/sys/kernel/core_pattern` points.

## Triage

```bash
scripts/uiux/crash-triage.sh --core <core> --binary <exact-executable> --output <crash.json>
scripts/uiux/crash-triage.sh --asan-log <sanitizer.log> --output <crash.json>
```

Exit `0` means no crash evidence was found, `1` reports a triaged crash, `2` is `HOLD` for a missing tool, core, binary, or log. The JSON matches the `assurance.py triage` shape: `boundary`, `category`, `uiux_owner`, `reason`, `frames`, `next_command`.

The binary must be the exact executable that produced the core. A mismatched binary yields plausible but wrong frames, which is worse than no backtrace; the script holds rather than guessing.

## Interpret

- `uiux_owner` is inferred from the first frame naming an owned tree (`qt`, `kit`, `wsd`, `common`, `net`, `rust`, `browser`). A null owner means the crash surfaced entirely in third-party frames; widen with `thread apply all bt` output before assigning blame.
- A release-build backtrace with inlined or missing frames is a `HOLD` for attribution, not proof of a third-party defect. Rebuild with symbols before concluding.
- ASAN claims require an ASAN-instrumented build. `scripts/probe-sanitizer-runtime.sh` verifies the toolchain can produce one; it does not prove the crash under test.
- A Rust-frame crash reaching the C ABI seam routes to `$axel-rust-engine-seam-audit` for boundary-contract review.

## Stop conditions

Return `HOLD` when the core, matching binary, symbols, or debugger is unavailable. Stop before production repair and report the crashing frame, owning layer, signal or sanitizer class, preserved evidence paths, and a bounded repair handoff. If repair is authorized, closure requires the crash reproduction and the original end-to-end scenario to both pass.
