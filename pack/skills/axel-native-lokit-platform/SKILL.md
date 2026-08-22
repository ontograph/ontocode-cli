---
name: axel-native-lokit-platform
description: Use when changes under common, kit, net, wsd, qt, or lo-patches cross native process, Qt6 desktop, Poco networking, process-isolation, LibreOfficeKit, or vendored LibreOffice boundaries.
license: MPL-2.0
metadata:
  owner: axel
  version: "1.0.0"
  scope: native/platform integration; UI test authoring has separate owners
---

# Axel Native LOKit Platform

## Boundary Rules

- Treat `vendor/lo-core` as upstream/vendor code. Product fixes belong in owned
  `common`, `kit`, `net`, `wsd`, or `qt` code unless the task explicitly approves
  a patch under `lo-patches`.
- The desktop build combines Qt6, QtWebEngine, Poco, zlib/zstd/png, custom
  sockets/WebSockets, child processes, seccomp/sidecars, and LibreOfficeKit.
  A change on one side can invalidate lifecycle assumptions on another.
- Before editing a lifecycle function, trace create/reopen/save/teardown paths
  and every caller. Do not fix only the crash or smoke scenario that exposed it.
- Preserve error propagation, PID/resource ownership, jail/path boundaries, and
  cleanup ordering. Never turn a native failure into a silently empty result.

## Workflow

1. Read the owning headers, corresponding Qt bridge/server call sites, and
   focused shell tests.
2. Classify the change as server protocol, kit/document lifecycle, Qt desktop
   adapter, packaging/runtime wiring, or vendor patch.
3. Implement the narrowest change consistent with both Linux server and direct
   Qt desktop execution.
4. Add evidence at the owning layer: focused shell test, launcher smoke, log/
   telemetry assertion, or native regression test.

## Lifecycle And Boundary Evidence

Walk the full matrix touched by the change: launch, document load, edit,
save-as/save, clean close, crash/failure, reopen, teardown, and restart. Record
the exact launcher binary and arguments, LibreOfficeKit/runtime version or
vendored patch, process/PID ownership, jail/path decisions, socket/session ID,
exit/cleanup order, and the observed log line for each transition.

Separate three claims explicitly: behavior supported in owned product code,
behavior delegated to LibreOffice, and behavior known to lack parity or require
a controlled `lo-patches` change. A vendor patch needs its upstream/base commit,
product trigger, rebuild evidence, and cleanup owner stated next to the test
result.

## Validation

Select repository-owned gates from the current change set:

```sh
scripts/select-gates.sh --run
```

For native/desktop-focused changes, start with focused coverage:

```sh
scripts/run-focused-coverage.sh --qt-only --required
```

When a local LibreOffice runtime is missing, use the repository builder rather
than inventing configure flags:

```sh
scripts/configure-ccache-build.sh --fresh-lo -- --enable-debug
```

Use `./run-qt.sh` for a real desktop launch under Xvfb when the change requires
runtime evidence. Report exact launcher arguments and observed logs.

## Routing

- Owning UI test selection: `$axel-select-uiux-tests`
- Real Qt scenarios: `$axel-run-qt-ui-scenarios`
- Native crashes/sanitizer output: `$axel-triage-native-crash`
- Engine migration readiness: `$axel-rust-engine-seam-audit`
