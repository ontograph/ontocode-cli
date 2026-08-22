---
name: axel-large-document-performance
description: Use when a change claims Axel large-workbook, native-grid, browser-rendering, WASM-kernel, soak, startup, memory, scalability, jank, latency, throughput, or large-document performance improvement.
license: MPL-2.0
metadata:
  owner: axel
  version: "1.0.0"
  scope: cross-stack performance evidence; not a substitute for functional tests
---

# Axel Large Document Performance

## Measurement Rules

Rank validity first, then memory/latency/throughput. A fast wrong answer is a
failure.

Freeze the fixture set and record checksums, dimensions, formula/cache profile,
hardware class, build SHA/worktree, environment variables, warm/cold mode, and
command for every comparison. Do not mix generated and committed fixtures unless
both sides consume identical bytes.

Use the narrowest existing harness before writing a new benchmark:

- Browser/native-grid budgets: `scripts/check-open-spreadsheet-budget.sh`,
  `scripts/measure-large-workbook-budget.py`, and
  `scripts/native-grid-perf-budget.py`.
- Fixture generation: `tools/bench-fixtures/`.
- Long-running behavior: bounded soak scripts under `scripts/`.
- Existing XL performance suite: `tools/xl-perf/run-suite.sh`.

## Workflow

1. Reproduce the regression with a bounded fixture and a measurable symptom.
   Gate investigation on that measurement; do not optimize from repo-wide search
   or intuition alone.
2. Profile before changing algorithms or allocations. Name the dominant frame,
   allocation site, render phase, IPC message, or decode stage.
3. Apply the smallest algorithm/data-structure change at the measured bottleneck.
4. Keep functional tests green and add one focused regression/budget assertion
   where the harness supports it.
5. Rerun baseline and candidate under the same conditions; discard runs whose
   setup differs.

Stop when validity fails, variance swamps the claimed delta, the measured
bottleneck disappears, the remaining gap is below the harness threshold, or the
candidate requires a functional trade-off the task did not authorize. State the
harness noise/variance policy rather than reporting a single lucky run.

## Evidence Format

For each candidate, report:

```text
fixture=<id> sha256=<hash>
baseline=<metric> candidate=<metric> delta=<value and percent>
runs=<count> command=<exact command>
functional=<pass/fail and focused suites>
verdict=<improved|neutral|regressed|invalid>
```

Do not generalize one fixture to all documents. State the row/column/formula
profile and stop condition.

## Routing

- Browser runtime profiling: `$axel-chrome-devtools-testing`
- Qt runtime scenarios: `$axel-run-qt-ui-scenarios`
- Python profiling utilities: `$axel-python-performance-optimization`
- Release qualification: `$axel-release-qualification`
