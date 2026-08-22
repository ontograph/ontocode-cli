# Axel Gate Profile

Use this profile only in the Axel repository.

## Evidence Location

Use the task's tracker-declared evidence directory. If none is declared, use
`build-scratch/evidence/<TASK_ID>/`. Record evidence paths in the owning tracker;
do not create a parallel `.protocols/` authority.

## Workflow

1. Read `AGENTS.md`, the task acceptance criteria, changed paths, and required
   validation from the owning tracker.
2. Run `scripts/select-gates.sh` to list the gates selected by the current
   change set. Use `--staged` only when verification is explicitly staged-only.
3. If C/C++ implementation files changed, confirm a usable merged
   `compile_commands.json`. Generate it with `scripts/gen-compile-db.sh` when a
   configured build tree exists. Missing compile data is a verification failure
   unless the task explicitly accepts and records that gap.
4. Run `scripts/verify-changed-no-binaries.sh` or `--staged-only` as applicable.
5. Run `scripts/select-gates.sh --run` for the path-owned gates. Add `--staged`
   when verification is staged-only. Do not wrap Python gates in Bash.
6. Run `project_plan_validate` when a project tracking plan changed.
7. Escalate only when the changed behavior requires it:
   - Qt/native grid: use the correctness mode from `qt-perf-monitor`.
   - Browser chrome: use the owning Mocha or Playwright check.
   - Rust engine boundary: use focused Rust, differential, and launcher proof.
   - Release artifacts: use `axel-release-qualification`.
8. Record each exact command, exit status, artifact path, skipped gate, and
   accepted validation gap. Do not convert an unrun command into a pass.

## Rust And C++ Selection

Select all applicable rows; a mixed Rust/C++ change must satisfy both sides.

| Changed surface | Required source evidence |
|---|---|
| Rust crate source or `Cargo.toml` | Run the crate's focused `cargo check` or `cargo test`. Run repository-selected format or lint gates when applicable. Record the manifest path and package or test target. |
| C/C++ outside `vendor/lo-core` | Use the merged `compile_commands.json`, then run the changed-source verifier and selected path gates. A server-only compile database does not cover `qt/`. |
| `qt/` C/C++ | Require compile data from a Qt-enabled tree. Add launcher correctness evidence only when behavior, rendering, input, or lifecycle changed. |
| `vendor/lo-core` C/C++ | Require the named target or test evidence produced with the preserved LibreOffice profile. Do not infer correctness from a full build or ccache hits. |
| Rust/C++ ABI or engine routing | Require focused Rust evidence, C++ caller/build evidence, and the slice-specific differential or launcher proof. Use `axel-rust-engine-seam-audit` for readiness, not as a substitute for execution evidence. |

Do not run a broad Cargo workspace, full LibreOffice build, or Qt launcher merely
because native files changed. Escalate only when the acceptance criteria or
changed behavior require that evidence.

## Issue-Fix Closeout

For a Rust, C++, or mixed-boundary defect, require all applicable evidence:

- The original focused command and its pre-fix failing result.
- The identical command passing after the fix. A substituted test is not
  red-to-green proof.
- The exact Rust manifest, package or target, and features when Cargo ran.
- Both focused Rust evidence and direct C++ caller/build evidence when the ABI
  or engine boundary changed.
- Expected files and symbols compared with the actual diff. Unexpected files,
  generated artifacts, or write-set violations fail verification until
  resolved or explicitly re-scoped by the task owner.
- Changed-source and selected-gate results after the focused command passes.

Do not require a pre-fix failure when the task is preventive rather than a bug
fix; record that classification instead of manufacturing a red result.

## Manager-Loop Closeout

When verifying a task integrated through the strict manager loop:

1. Run `project_plan_validate` against the owning tracking file even when the
   task did not edit that file.
2. Run `gn_verify_diff` with the task's expected files, symbols, and executed
   tests. Treat stale OntoIndex evidence as provisional until refreshed.
3. Match the integrated task ID, dispatch revision, and authenticated receipt
   to the tracker evidence. A result without the required receipt cannot pass.
4. Record the final task state and the existing recovery counters:
   `evidence_corrections`, `rejected_receipts`,
   `consecutive_touches_without_completion`, `disk_recoveries`, and
   `background_job_resumptions`.
5. Produce one manager-loop closeout verdict containing acceptance-criteria
   results, selected source gates, plan validation, diff verification, receipt
   identity, recovery counters, evidence paths, and remaining gaps.

Do not create a separate closeout ledger; write the verdict in the owning
tracker's declared evidence location.

## Verdict

- `PASS`: every required gate for the task ran and passed.
- `PARTIAL`: source checks pass but required runtime or external evidence is
  pending and the tracker permits partial verification.
- `FAIL`: a required gate fails, evidence is invalid, or compile coverage is
  missing without explicit acceptance.

Keep ccache evidence separate from correctness; cache hits are not a test.
