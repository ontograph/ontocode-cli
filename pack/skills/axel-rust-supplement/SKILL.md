---
name: axel-rust-supplement
description: >
  Overlay for the axel-rust-standard base covering Axel's C ABI lifecycle, native
  build verification, semantic boundary values, reproducible evaluation, Pin,
  panic strategy, and supply-chain gates. Use together with axel-rust-standard
  whenever writing or reviewing Rust in this workspace, especially for axel-ffi
  and Qt integration. Also defines precedence for this workspace's edition, MSRV,
  and measure-first rules.
license: MPL-2.0
metadata:
  owner: axel
  version: "1.1.0"
  base_skill: axel-rust-standard (vendored leonardomso/rust-skills v1.5.1)
  scope: gaps and overrides only, not a replacement standard
---

# Axel Rust Supplement

`axel-rust-standard` is the base: 265 compile-verified rules covering ownership,
errors, async, unsafe, memory, and API design. Keep using it. This overlay adds the
categories it has no rules for, and states where its advice must not be followed
verbatim in this workspace.

## Precedence

When this skill and `axel-rust-standard` disagree, this skill wins. Three standing
overrides:

1. **Edition and MSRV.** The base standard targets Rust 1.96 / edition 2024. This
   workspace is `edition = "2021"`, `rust-version = "1.70"` (see
   `rust/Cargo.toml`). Reject any rule requiring a newer edition or a `std` API
   stabilized after 1.70: `unsafe extern {}` blocks, `#[unsafe(no_mangle)]`,
   `gen` blocks, `let`-chains, and native `async fn` in traits are all out of
   scope until the workspace bumps. Bare `#[no_mangle]` is correct here.
2. **Crate suggestions require measurement.** `mem-smallvec`, `mem-thinvec`,
   `mem-compact-string`, `mem-arrayvec`, and `perf-ahash` propose new
   dependencies. Do not add one without a benchmark showing the stdlib type is
   the bottleneck. See `rules/measure-before-optimize.md`.
3. **The `opt-*` category is measure-first.** `opt-inline-always-rare`,
   `opt-likely-hint`, `opt-target-cpu`, `opt-pgo-profile`, and friends are
   tuning levers, not defaults. `perf-profile-first` governs all of them.

## Routing

| Situation | Go to |
|---|---|
| General Rust writing, review, refactor | `axel-rust-standard` |
| Anything crossing `extern "C"` | this skill, `ffi-*` rules |
| Cargo artifacts consumed by Qt or another native build | this skill, `cargo-native-verification` |
| Boundary inputs with optional or same-typed fields | this skill, `semantic-boundary-values` |
| Comparing Rust implementations or model output | this skill, `rust-evaluation-reproducibility`, `benchmark-api-stability` |
| Claiming a Rust artifact is reproducible | this skill, `artifact-provenance` |
| Comparing the workbook engine with its sealed oracle | this skill, `oracle-parity-freshness` |
| `Pin`, `Box::pin`, self-referential futures | this skill, `pin-*` rules |
| Dependency/CVE/SemVer gates | this skill, `supply-*` rules |
| Auditing the Axel engine boundary end to end | `axel-rust-engine-seam-audit` |

`axel-rust-engine-seam-audit` is the authority for Axel engine-migration audits
(ABI failure shield, differential oracle, rollback). This skill covers how to
*write* boundary code; that skill covers whether a slice is *ready to ship*. Do
not use this skill to approve a default-engine flip.

## Rules

### FFI and the C ABI boundary (CRITICAL)

- [`ffi-no-unwind-boundary`](rules/ffi-no-unwind-boundary.md) - wrap every `extern "C"` body in `catch_unwind`; unwinding across the boundary is UB
- [`ffi-abort-profile-conflict`](rules/ffi-abort-profile-conflict.md) - `panic = "abort"` silently disables every `catch_unwind` shield
- [`ffi-repr-c-layout`](rules/ffi-repr-c-layout.md) - `#[repr(C)]` on every type crossing the boundary; never expose a default-layout type
- [`ffi-opaque-handle-ownership`](rules/ffi-opaque-handle-ownership.md) - pair `Box::into_raw` with exactly one `Box::from_raw` free function
- [`ffi-validate-raw-input`](rules/ffi-validate-raw-input.md) - null-check and UTF-8-validate every incoming pointer before use
- [`ffi-error-out-of-band`](rules/ffi-error-out-of-band.md) - return a stable status code; carry detail in a separate last-error channel
- [`ffi-contract-lifecycle`](rules/ffi-contract-lifecycle.md) - verify declarations, errors, mutations, and polling as one cross-language lifecycle

### Pin and self-referential futures

- [`pin-self-referential`](rules/pin-self-referential.md) - use `Box::pin` when a future or struct holds a pointer into itself
- [`pin-no-move-out`](rules/pin-no-move-out.md) - never move a value out of a `Pin<&mut T>` unless `T: Unpin`

### Panic strategy

- [`panic-strategy-declare`](rules/panic-strategy-declare.md) - declare unwind vs abort per profile and know which crates depend on it

### Native build and verification

- [`cargo-native-verification`](rules/cargo-native-verification.md) - prove Cargo work, native artifact freshness, test selection, and verification escalation

### Boundary semantics

- [`semantic-boundary-values`](rules/semantic-boundary-values.md) - preserve field meaning and absence instead of inventing interchangeable defaults

### Evaluation integrity

- [`rust-evaluation-reproducibility`](rules/rust-evaluation-reproducibility.md) - freeze byte-identical inputs and rank correctness before speed
- [`benchmark-api-stability`](rules/benchmark-api-stability.md) - keep declared public APIs unchanged during comparative implementation work
- [`artifact-provenance`](rules/artifact-provenance.md) - qualify checksums with freshness, metadata, and deterministic-build caveats
- [`oracle-parity-freshness`](rules/oracle-parity-freshness.md) - prove sealed-oracle inputs and Rust/native artifacts are fresh before comparison

### Supply chain

- [`supply-cargo-deny`](rules/supply-cargo-deny.md) - gate licenses, bans, and advisories with `cargo-deny` in CI
- [`supply-cargo-audit-ci`](rules/supply-cargo-audit-ci.md) - fail CI on known RUSTSEC advisories
- [`supply-semver-checks`](rules/supply-semver-checks.md) - run `cargo-semver-checks` before publishing a library bump

### Overrides

- [`msrv-edition-guard`](rules/msrv-edition-guard.md) - verify every suggested API against edition 2021 / Rust 1.70
- [`measure-before-optimize`](rules/measure-before-optimize.md) - no new dependency and no codegen lever without a profile first

## Quick Reference

- Panic crossing `extern "C"` is undefined behavior, not a crash you can debug.
- `catch_unwind` + `panic = "abort"` is a false sense of safety; both must agree.
- Edition 2024 unsafe syntax does not compile here. Check MSRV before citing a rule.
- A crate suggestion without a benchmark is a dependency you will maintain for nothing.
- A matching checksum does not prove source lineage or that an artifact is fresh.
