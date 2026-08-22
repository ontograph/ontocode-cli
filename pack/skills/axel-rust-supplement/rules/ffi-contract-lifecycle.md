# Verify the Complete FFI Contract Lifecycle

Treat the ABI as a cross-language state machine. Rust declarations, C headers,
ownership, errors, mutations, and polling must describe the same lifecycle.

## Why It Matters

A locally correct `extern "C"` function can still corrupt callers when the
header drifts, stale error state survives success, a rejected mutation partly
applies, or a polling result outlives its buffer.

## Required Checks

- Mechanically compare mirrored declarations: calling convention, field order
  and types, enum values, and opaque-handle shape. Use compiler assertions for
  size, alignment, and offsets when ABI layout is release-critical.
- Clear stale error state at entry. On failure, set a stable typed code and a
  diagnostic; on success, leave both clear.
- Decode and validate a complete request before changing workbook state or
  caller-owned output buffers. Rejection and caught panic must be fail-atomic.
- Define polling states (`pending`, `ready`, `failed`, `cancelled`), terminal
  behavior, retry rules, idempotent cancellation, and buffer ownership.
- Give every deliberately unmirrored symbol an explicit allowlist rationale.

## In This Workspace

Run `scripts/check-rust-ffi-contract.sh`. Review
`rust/crates/axel-ffi/src/lib.rs`,
`rust/crates/axel-ffi/include/axel_workbook.h`, and the Qt adapter together.
The static gate complements sanitizer and soak tests; it does not replace them.

## See Also

`ffi-no-unwind-boundary`, `ffi-repr-c-layout`,
`ffi-opaque-handle-ownership`, `ffi-error-out-of-band`.
