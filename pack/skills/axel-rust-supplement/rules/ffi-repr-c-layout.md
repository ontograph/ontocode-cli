# ffi-repr-c-layout

> Put `#[repr(C)]` on every type that crosses the boundary; never expose a default-layout type

## Why It Matters

Rust's default representation gives the compiler freedom to reorder fields, choose
niche-optimized discriminants, and change layout between compiler versions. None of
that is stable ABI. A C header that describes a default-layout struct is describing a
layout that may not survive a toolchain bump, and the mismatch shows up as silently
wrong field values rather than a link error.

`#[repr(C)]` pins field order and padding to the platform C rules. For enums crossing
the boundary you also need an explicit integer representation so the discriminant
width is defined.

## Bad

```rust
// Default layout: field order is not guaranteed, so the C side may read garbage.
pub struct ProbeResult {
    pub ok: bool,
    pub file_size_bytes: u64,
    pub entry_count: u32,
}

// Default enum: discriminant type is unspecified across the ABI.
pub enum EngineError {
    Ok,
    NotFound,
}

#[no_mangle]
pub extern "C" fn probe() -> ProbeResult {
    ProbeResult { ok: true, file_size_bytes: 0, entry_count: 0 }
}
```

## Good

```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct ProbeResult {
    pub ok: bool,
    pub file_size_bytes: u64,
    pub entry_count: u32,
}

// Explicit width: the C side declares a matching int32_t-backed enum.
#[repr(i32)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum EngineError {
    Ok = 0,
    NotFound = 1,
    Internal = 2,
}

#[no_mangle]
pub extern "C" fn probe() -> ProbeResult {
    ProbeResult::default()
}
```

## Key Points

- Only FFI-safe field types belong in a `#[repr(C)]` boundary struct: integers,
  floats, `bool`, raw pointers, and other `#[repr(C)]` types. A `String`, `Vec<T>`,
  `Option<T>`, or trait object in a boundary struct is a bug even if it compiles.
- Use `#[repr(transparent)]` for a newtype that must have the identical ABI as its
  single field.
- Enable `improper_ctypes_definitions` (on by default) and never `allow` it to
  silence a layout complaint; the lint is usually right.
- Keep the C declaration and the Rust definition in sync mechanically where possible.
  A hand-maintained header drifts.

## In This Workspace

`rust/crates/axel-ffi/src/lib.rs` marks every boundary struct `#[repr(C)]`
(`AxelXlsxProbeResult`, `AxelByteBuffer`, and the rest) and keeps string-heavy
workbook data out of FFI entirely until the ownership contract is reviewed, as the
module docs state. Follow that restraint: value-only crossings first.

## See Also

- [ffi-opaque-handle-ownership](ffi-opaque-handle-ownership.md) - passing non-trivial state instead
