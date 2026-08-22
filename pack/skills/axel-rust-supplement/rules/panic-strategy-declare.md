# panic-strategy-declare

> Decide unwind vs abort deliberately per profile, and know which crates depend on the choice

## Why It Matters

The panic strategy is usually inherited by accident. It changes binary size, whether
destructors run during a panic, and whether `catch_unwind` works at all - three
unrelated consequences from one line of TOML. Teams discover the coupling when a
library that promised recoverable errors starts killing the host process.

Decide once, write it down, and treat a change as an API-affecting decision.

## Bad

```toml
# Copied from a blog post about smaller binaries. Nobody checked what depends
# on unwinding, and the workspace exports a C ABI that catches panics.
[profile.release]
panic = "abort"
opt-level = "z"
```

## Good

```toml
# rust/Cargo.toml
#
# Panic strategy: unwind (the default) for all profiles.
# Rationale: axel-ffi shields its extern "C" entry points with catch_unwind and
# converts panics into AxelEngineError. Switching to abort would silently
# disable those shields, so it is an ABI-contract change, not a size tweak.
[profile.release]
lto = true
codegen-units = 1
```

## Key Points

- Under `abort`, destructors do not run during a panic. Anything relying on `Drop` for
  flushing or releasing an external resource loses that guarantee.
- `abort` is reasonable for a leaf binary with no panic-recovery contract and real
  size pressure. It is wrong for a `cdylib`/`staticlib` with a catching boundary.
- The strategy can also be set via `RUSTFLAGS="-C panic=abort"` outside the manifest;
  audit both when verifying.
- Record the rationale next to the setting. The next size-reduction pass will
  otherwise repeat the mistake.

## In This Workspace

No `panic` key appears in `rust/Cargo.toml` or the member manifests, so the workspace
builds with unwind and `axel-ffi`'s shields are effective. Treat any proposal to set
`panic = "abort"` as a change to the engine's error contract and route it through
`axel-rust-engine-seam-audit`.

## See Also

- [ffi-abort-profile-conflict](ffi-abort-profile-conflict.md) - the concrete failure this prevents
