---
name: axel-rust-engine-seam-audit
description: Audit Axel Rust workbook-engine integration at the C ABI, desktop engine boundary, Qt build wiring, differential-oracle gates, and rollback path. Use when reviewing a C++ to Rust workbook migration, investigating Rust-backed desktop crashes or missing behavior, challenging an engine plan, or checking whether a Rust engine slice is ready to become default. This is audit-first; make code changes only when explicitly requested.
---

# Axel Rust Engine Seam Audit

Find boundary defects and missing proof in the live repository. Prefer one owning-layer correction over caller-by-caller patches.

## Evidence First

1. Read the repository `AGENTS.md` and the current Rust FFI, engine-swap, and recovery ADR or plan documents relevant to the requested slice.
2. Check OntoIndex freshness. Refresh once when stale, then use semantic search and symbol context to trace the real creation, selection, call, and teardown flows.
3. Verify graph claims in current source and build files. Treat missing or stale evidence as provisional, not clean.
4. Audit without editing by default. If a fix is requested, run impact analysis on the owning symbol before making the smallest source change.

## Audit Surfaces

### C ABI failure shield

- Enumerate exported Rust functions and their C/C++ callers.
- Confirm no Rust panic or C++ exception can cross the ABI boundary.
- Confirm `catch_unwind` covers panic-capable work and all failures become stable status/error data.
- Flag any `panic = "abort"` profile used by a library that relies on `catch_unwind`.
- Check null pointers, lengths, UTF-8 or byte ownership, allocator symmetry, free functions, and handle lifetime.

### Desktop engine routing

- Trace engine construction, `--engine` selection, command routing, rendering, save, and teardown through `DesktopWorkbookEngine`.
- Find direct `_workbookHandle.lokitDocument()` or equivalent LOKit assumptions reachable when Rust is selected. A Rust-backed runtime must use engine methods instead of requiring a LOKit document.
- Verify error paths fail visibly; do not permit a hidden LOKit or browser-grid fallback.

### Build and package wiring

- Check `qt/Makefile.am`, especially `coda_qt_SOURCES`, for every required adapter translation unit.
- Verify the Rust library is actually linked and packaged. File existence alone is not build proof.
- Check launcher argument forwarding and runtime evidence for the selected engine.

### Golden oracles and rollback

- Confirm current-engine golden values were recorded before replacement work.
- Match proof to the slice: formula differential, workbook round-trip, XLSX package-path comparison, focused unit tests, and real Qt launcher evidence where desktop behavior changes.
- Do not use `cargo miri` as a default gate on Axel's stable toolchain.
- Confirm the old engine remains selectable after the replacement becomes default and that the flag flip was rehearsed and timed. Do not approve deletion of the old path in the same change that makes the new one default.

## Handoffs

Keep this skill audit-first and route execution to the existing owner:

| Need | Owner |
|---|---|
| Implement an accepted Rust/C++ correction | `mb-execute`, using its Axel native-iteration reference |
| Verify completed Rust, C++, Qt, or LibreOffice changes | `mb-verify`, using its Axel gate profile |
| Diagnose a compile, link, profile, or runtime failure | `diagnosing-bugs`, using its Axel native-build triage reference |
| Watch an existing long build or validation | `axel-background-job-watch` |
| Decide readiness, differential proof, default selection, or rollback safety | Remain in this skill |
| Diagnose a Rust-frame crash reaching the C ABI | `axel-triage-native-crash`, then return here for boundary-contract review |

Do not perform implementation, general build orchestration, or task closeout in
this audit merely because the audit found the need.

## Rust Test Authoring

This skill is the authority for how Rust engine tests are written, so authoring
rules and seam rules cannot drift apart.

Run focused, not whole-workspace. Use `CARGO_BUILD_JOBS=8` on this host; an
unbounded parallel build starves the machine during Qt work:

```bash
CARGO_BUILD_JOBS=8 cargo test -p axel-core --lib <module>::
CARGO_BUILD_JOBS=8 cargo test -p axel-ffi --test <integration-test>
CARGO_BUILD_JOBS=8 cargo test -p axel-xlsx
```

Place each test where its truth lives:

- `axel-core`: pure engine logic. Unit tests next to the code; property tests
  (`proptest`) only for the formula parser and evaluator, where the input space
  is genuinely unbounded. Elsewhere table-driven cases are cheaper to read and
  cheaper to debug than a shrunk counterexample.
- `axel-ffi`: boundary behaviour. Every test must cover a failure path, not only
  the success path: null pointers, invalid UTF-8, ownership transfer, and panic
  containment at the shield. A passing FFI suite that never exercises a failure
  proves the shield compiles, not that it holds.
- `axel-xlsx`: package round-trip. Assert structured readback, never string
  equality of serialized XML.

Differential claims against LibreOffice go through the existing oracle rather
than a hand-written expectation: `scripts/check-rust-oracle-parity.sh` for
parity, `scripts/record-lo-oracle.py` to capture a new baseline, and
`scripts/seal-oracle-manifest.py` to freeze it. A new oracle baseline is
evidence only once sealed; an unsealed baseline can drift under you.

Closeout follows `mb-verify`'s red-to-green rule: show the test failing against
the unfixed source before showing it pass. A test that was never red proves
nothing about the fix.

## Findings

Lead with findings ordered by severity. For each finding provide:

- File and line or symbol.
- The violated boundary or missing evidence.
- The reachable failure mode and affected flow.
- The smallest owning-layer correction or proof required.

Then state verified strengths, unresolved questions, and a readiness verdict: `READY`, `PARTIAL`, or `BLOCKED`. Never return `READY` from source inspection alone when runtime, differential, or rollback evidence is required.
