---
name: qt-perf-monitor
description: Run bounded Axel/CODA Qt launcher checks in performance or native-grid correctness mode. Use when asked to execute run-qt.sh, monitor CPU/RSS, collect Qt process samples, validate the native grid through real launcher evidence, or prove browser-grid fallback is absent.
---

# Qt Perf Monitor

Use one explicit mode:

- `performance`: collect a bounded CPU/RSS smoke report with the bundled script.
- `correctness`: read `references/axel-native-grid-qualification.md` and run the
  smallest repository-owned runtime proof for the changed behavior.

## Default workflow

1. Confirm you are at the repository root containing `run-qt.sh`.
2. Prefer the bundled script; do not hand-roll sampling unless the script is missing.
3. Run the default 3-minute monitor:

```bash
~/.codex/skills/qt-perf-monitor/scripts/run_qt_perf_monitor.sh --repo /home/er77/_wrk/axel
```

4. If a shorter validation is needed, override duration:

```bash
~/.codex/skills/qt-perf-monitor/scripts/run_qt_perf_monitor.sh --repo /home/er77/_wrk/axel --duration 30 --interval 5
```

5. Report:
   - output directory;
   - whether `./run-qt.sh` started successfully;
   - `coda-qt`, `coolwsd`, `coolforkit`/kit, and `QtWebEngine` average/max CPU and RSS;
   - any launch errors from `run-qt.log`;
   - whether the run is a smoke signal only or enough evidence for the user’s decision.

## Script behavior

The script:

- starts `./run-qt.sh`;
- samples likely Qt/COOL processes every 5 seconds by default;
- stops the launched process group after 180 seconds by default;
- writes artifacts to `tools/runtime-trace/artifacts/qt-perf-monitor/<UTC timestamp>/`;
- prints `SUMMARY.md` with a process table.

Artifacts:

```text
SUMMARY.md
process-samples.tsv
process-summary.md
run-qt.log
meta.env
runner.pid
```

## Safety notes

- This is a dev smoke monitor, not a production benchmark.
- Use `LIVE_SERVER=1` default behavior from `run-qt.sh` unless the task says otherwise.
- Pass `--qt-log-level information` or set `QT_LOG_LEVEL=information` to surface `QT_WEBVIEW_LOAD_FINISHED`.
- Use `--threads` when you need thread-level `ps -L` sampling and `thread-samples.tsv`.
- If the launcher fails because Qt/build artifacts are missing, report the exact missing path and suggested build command from `run-qt.log`.
- Do not claim performance regressions from one 3-minute smoke; classify as `PASS`, `FAIL_TO_LAUNCH`, `NEEDS_LONGER_RUN`, or `OBSERVE_SPIKE`.
- Performance evidence never proves native-grid correctness. A correctness pass
  requires launcher, visual, interaction, and lifecycle evidence from the
  repository-owned qualification profile.

## Passing extra run-qt args

Pass arguments after `--`:

```bash
~/.codex/skills/qt-perf-monitor/scripts/run_qt_perf_monitor.sh --repo /home/er77/_wrk/axel -- --some-run-qt-arg
```

## Routine Tool Ownership

This skill owns routine-tool operations 34-35 in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Release
and native-grid probes must record command matrix, build/runtime identity,
artifacts, and pass/fail state in the coordinator's shared envelope.
