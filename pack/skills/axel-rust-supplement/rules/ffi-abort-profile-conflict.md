# ffi-abort-profile-conflict

> `panic = "abort"` silently disables every `catch_unwind` shield in the build

## Why It Matters

`catch_unwind` only catches an *unwinding* panic. Under `panic = "abort"` a panic
terminates the process immediately and the handler never runs. The code still
compiles, the tests that exercise the happy path still pass, and the boundary looks
defended in review. The first panic in production kills the host application.

This is a build-profile decision that invalidates source-level safety, so it cannot
be caught by reading the boundary file alone. Check the profile whenever you audit a
`catch_unwind`.

## Bad

```toml
# Cargo.toml - a library whose C ABI depends on catching panics
[profile.release]
panic = "abort"        # every catch_unwind in this crate is now dead code
lto = true
```

```rust
// Looks defended. Under the profile above, this handler is unreachable.
#[no_mangle]
pub extern "C" fn wb_open(path: *const std::os::raw::c_char) -> bool {
    std::panic::catch_unwind(|| {
        do_open(path) // panics here abort the process
    })
    .unwrap_or(false)
}
# fn do_open(_: *const std::os::raw::c_char) -> bool { true }
```

## Good

```toml
# Keep unwind for any profile that builds a panic-shielded ABI.
[profile.release]
lto = true
codegen-units = 1
# panic defaults to "unwind" - do not set "abort" here

# If binary size or codegen pressure forces abort, it must be scoped to
# binaries that do NOT export a C ABI, never to the shielded library.
```

## Key Points

- Grep for `panic = "abort"` in the workspace manifest, every member manifest, and
  any `.cargo/config.toml` before trusting a `catch_unwind`.
- `-C panic=abort` passed through `RUSTFLAGS` has the same effect and is easier to
  miss because it lives outside the manifests.
- Abort is a legitimate choice for a leaf binary. It is not a legitimate choice for
  a `staticlib`/`cdylib` that promises the host "errors come back as status codes".
- Tests run under a different profile than release. A green `cargo test` says nothing
  about whether the shipped artifact unwinds.

## In This Workspace

`rust/Cargo.toml` and the three member manifests declare no `panic` setting, so
`axel-ffi` builds with unwind and its `catch_unwind` shields are live. Any change
that introduces `panic = "abort"` must be treated as an ABI-contract change, not a
build tweak.

## See Also

- [ffi-no-unwind-boundary](ffi-no-unwind-boundary.md) - the shield this rule protects
- [panic-strategy-declare](panic-strategy-declare.md) - choosing a strategy deliberately
