---
name: axel-background-job-watch
description: Monitor an existing long-running Axel build or validation job through its PID, log, and optional status file without repeated manual polling. Use when asked to watch, wait for, monitor, or summarize a LibreOffice build, background validation, package job, or other bounded Axel command already running.
---

# Axel Background Job Watch

Watch one existing process to a terminal state and emit compact evidence.

## Workflow

1. Require a PID and log path. Accept an optional status file produced by `scripts/bg-run.sh` or another repository helper.
2. Do not start a second build or equivalent command while the first is alive.
3. Run the bundled watcher with a bounded timeout and interval.
4. Treat log growth or status-file change as progress. Avoid printing unchanged log tails.
5. On process exit, read the terminal status and final relevant log lines once.
6. If no state changes occur for the configured stall window, report `STALLED`; do not kill the process unless explicitly requested.
7. For builds, preserve the repository limits: shared ccache and at most `-j8`.

## Script

```bash
python3 ~/.ontocode/skills/axel-background-job-watch/scripts/watch_job.py \
  --pid PID --log PATH [--status PATH] [--timeout 3600]
```

The script prints newline-delimited JSON state changes followed by one summary object. Use `--quiet` for the summary only.

## Evidence

Report the PID, paths, elapsed time, terminal classification, exit code when known, final log size, number of progress changes, and final relevant log lines. Classify the result as `COMPLETED`, `FAILED`, `TIMED_OUT`, `STALLED`, or `MISSING`.
