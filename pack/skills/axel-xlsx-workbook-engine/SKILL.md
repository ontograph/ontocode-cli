---
name: axel-xlsx-workbook-engine
description: Use when changes touch rust/crates, workbook fixtures, spreadsheet engine integration, XLSX/OOXML parsing or serialization, formula/error semantics, workbook round trips, or Axel's Rust workbook-engine FFI contract.
license: MPL-2.0
metadata:
  owner: axel
  version: "1.0.0"
  scope: native workbook engine and XLSX semantics, not generic office-document rendering
---

# Axel XLSX Workbook Engine

## Invariants

- `rust/crates/axel-core`, `axel-xlsx`, and `axel-ffi` form the native engine.
  Keep core semantics independent of FFI and keep ABI types stable.
- XLSX is a ZIP/OOXML contract. Structural loss, dropped defined names, changed
  formula cells, merged ranges, tables, cached errors, and sheet identity are
  behavioral failures, not cosmetic diffs.
- Every public C ABI crossing needs explicit ownership, validation, error
  reporting, unwind shielding, and mirrored declarations.
- Fixture files may contain user-like content. Generate synthetic fixtures for
  new cases and avoid committing private workbook data.

## Workflow

1. Reduce the report to workbook structure, formulas, values, cached results,
   styles/dimensions when behaviorally relevant, and expected round-trip state.
2. Find the shared parser/serializer/ABI function that owns the behavior before
   patching a caller.
3. Add a minimal fixture or deterministic constructor plus a focused Rust test.
4. Update the FFI header/contract and Qt consumer together when the ABI surface
   changes.

## Validation

Run the workspace:

```sh
CARGO_BUILD_JOBS=8 cargo test --manifest-path rust/Cargo.toml --workspace
```

Enforce monotone lint and panic-path budgets:

```sh
scripts/check-rust-lint-gate.sh
scripts/check-rust-unwrap-ratchet.sh
```

Prove the ABI and round-trip contracts:

```sh
scripts/check-rust-ffi-contract.sh
bash scripts/tests/workbook-roundtrip.test.sh
```

For a concrete workbook, add `scripts/check-workbook-roundtrip.py` only after
checking its CLI contract; do not treat structural equality as value/formula
equality unless that check actually covers it.

## Formula Semantics

Keep formula text, parsed formula, cached value, cached error type, recalculation
result, and display formatting distinct. A successful recalculation proves only
that evaluation completed; it does not prove function arguments, references,
locale-independent parsing, external-link resolution, or user-visible formatting
match the source workbook.

A structural round trip is insufficient when formulas are involved. Assert the
intended subset explicitly: formula text and parse tree where applicable, cached
value/error preservation, dependency graph, defined names, sheet/table identity,
external-link target policy, and post-recalc values. For an imported fixture,
record its origin and SHA-256; for generated fixtures, keep the constructor under
test ownership.

## Routing

- Rust standards: `$axel-rust-standard`
- FFI/native build overlay: `$axel-rust-supplement`
- Migration audit: `$axel-rust-engine-seam-audit`
- External workbook inspection: `$excel`
