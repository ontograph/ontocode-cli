---
name: axel-wasm-data-kernels
description: Use when changing or reviewing browser/wasm Rust/WASM kernels or their Node/browser interop boundary, especially wasm-pack, wasm-bindgen, Arrow, binary frames, channel codecs, tile decoding, Zstandard, property tests, or benchmarks.
license: MPL-2.0
metadata:
  owner: axel
  version: "1.0.0"
  scope: browser/wasm kernels and JavaScript interop, not native rust/crates engine code
---

# Axel WASM Data Kernels

## Stack Facts

- Kernel crates live under `browser/wasm`. They compile as `cdylib` plus
  `rlib`, use `wasm-bindgen`, and are built with wasm-pack for Node tests where
  the npm scripts require it.
- Release profiles intentionally use small binary settings (`opt-level = "s"`,
  LTO enabled) and commonly disable `wasm-opt`. Do not reverse these choices
  without a byte-size and runtime measurement.
- Data-path crates include Arrow handling, binary frames, channel codecs,
  FlatBuffer reading, row-window packing, reset behavior, and tile decoding.
  Keep framing, compression, and allocation semantics aligned across Rust,
  TypeScript, and fixtures.

## Workflow

1. Identify the kernel and both sides of the boundary: Rust input/output shape
   and the TypeScript caller or fixture.
2. Preserve explicit failure behavior for malformed frames, truncated input,
   unsupported versions, allocation failure, and decompression errors.
3. Prefer changing the smallest kernel API. Do not add a new codec or dependency
   without a failing case and measured need.
4. Add a focused proptest or deterministic unit test for malformed and valid
   inputs. Use criterion only when timing or allocation behavior changed.

## Malformed-Input Matrix

Before declaring boundary handling complete, name the outcome for each class the
touched decoder owns: empty input, truncated header/body, declared-versus-actual
length mismatch, unsupported version/type, invalid UTF-8 where text is accepted,
decompression failure, integer overflow, null/empty vector policy, and repeated
or out-of-order frames. A panic, error code, rejected callback, and silently
ignored frame are different contracts; preserve the one owned by the caller.

## Measurement Guardrails

For size or runtime work, compare one frozen fixture at a time. Record fixture
checksum, `.wasm` byte count, exact build command, runtime metric, and both
crate versions. Do not copy generic advice such as `opt-level = "z"`,
`panic = "abort"`, thin LTO, or enabling `wasm-opt`: first read this checkout's
profile and prove the proposed profile preserves correctness, exception/boundary
behavior, startup latency, and steady-state throughput.

## Validation

Build and run the Node-visible kernel suite:

```sh
cd browser && npm run build-wasm-nodejs && npm run test-wasm
```

Run the touched crate directly:

```sh
cargo test --manifest-path browser/wasm/<crate>/Cargo.toml
```

For benchmark-backed changes, record baseline and candidate output separately
and compare correctness before speed.

## Routing

- General Rust rules: `$axel-rust-standard`
- Native engine ABI: `$axel-rust-supplement`
- Browser language conventions: `$axel-typescript-development`
