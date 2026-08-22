# Verify Cargo Work Through the Native Consumer

A successful Cargo command is insufficient when native build graphs, shared
target directories, test filters, or persisted artifacts can be stale.

## Required Checks

- Bound parallel work with `CARGO_BUILD_JOBS`; isolate concurrent worktrees or
  experiments with distinct `CARGO_TARGET_DIR` values.
- Make native artifact targets depend on recursive Rust sources, all relevant
  manifests, `Cargo.lock`, `build.rs`, and generated inputs.
- Prove the recipe produced the artifact at the path the native linker consumes.
  Never `touch` an expected output that Cargo may have written elsewhere.
- Before an exact test filter, list qualified tests and fail when zero match.
- Preserve Cargo exit status through pipelines with `set -euo pipefail`.
- Escalate evidence from focused test, to crate, to affected workspace and
  native consumer. Persistent mutations also require save, clean close, reopen,
  and a structured-value oracle.

## In This Workspace

Run `scripts/check-rust-native-build-deps.py` after editing `qt/Makefile.am` or
the Rust workspace. Use `CARGO_BUILD_JOBS=8` for the standard verification set
unless the active environment requires a lower bound.
