# Axel Native Iteration

Use this reference only in the Axel repository for Rust, C++, Qt, or
LibreOffice implementation tasks.

## Preflight

1. Read the task's allowed write set and validation commands.
2. Identify the owning surface: Rust crate, ordinary C++, Qt, LibreOffice, or a
   Rust/C++ boundary. Use every applicable surface for mixed changes.
3. Export `CCACHE_DIR=/home/er77/_wrk/.cache/ccache-axel` and keep all build or
   test commands at `-j8` or lower. Verify `ccache -p` before a long build.
4. If an equivalent build or validation process is alive, route it to
   `axel-background-job-watch`; do not start another.

## Choose The Narrowest Command

- **Rust:** locate the owning `Cargo.toml`; run the affected package or test
  target with `--manifest-path` when needed. Prefer `cargo check` or one focused
  `cargo test` before broader Cargo work. Run format or Clippy only when the
  repository gate or task requires it.
- **Ordinary C++:** default to source-only iteration. Do not produce binaries
  unless the task requires a compiled test or runtime result. Leave final
  changed-file and compile-database qualification to `mb-verify`.
- **Qt C++:** use a Qt-enabled configured tree for compile data. Run a focused
  Qt test when one owns the behavior; use the real launcher only for required
  runtime evidence.
- **LibreOffice C++:** preserve `vendor/lo-core/workdir` and `instdir`. Keep the
  configured `runtime` or `tiled-test` profile unchanged. Run one named gbuild
  target or `CPPUNIT_TEST_NAME`; use `--no-clean` when the repository helper
  must prove the profile contract.
- **Rust/C++ boundary:** run the focused Rust command and the owning C++ build or
  test. Do not treat one side compiling as proof that linkage, ownership, or
  runtime routing works.

Reserve `--fresh-lo`, full native builds, and launcher runs for explicit clean,
runtime, or release evidence. Record the selected surface, profile, target,
command, exit status, and evidence path in the task's existing tracker.

## Bounded Issue-Fix Loop

For a reported Rust, C++, or mixed-boundary defect:

1. Run one focused command that reproduces the exact issue and record its
   failing output. If the command is blocked before product code runs, route to
   `ontocode-tool-contract-preflight` instead of changing source.
2. Patch the smallest owning layer within the allowed write set. For an ABI
   defect, fix the shared boundary owner rather than every caller.
3. Rerun the identical focused command. Do not replace it with a broader test
   or a different assertion to obtain a pass.
4. After it passes, run the changed-source verifier and path-selected gates
   declared by the task, then hand off to `mb-verify`.

If the same first owning failure survives two consecutive source attempts
without new evidence, stop patching, record both attempts, and route to
`diagnosing-bugs`. Do not widen the write set merely to continue the loop.

## Stop And Route

- Compile or link failure: use `diagnosing-bugs` with its Axel native-build
  triage reference.
- Rust engine readiness or rollback question: use
  `axel-rust-engine-seam-audit`.
- Running long command: use `axel-background-job-watch`.
- Completed implementation: hand off to `mb-verify`.
