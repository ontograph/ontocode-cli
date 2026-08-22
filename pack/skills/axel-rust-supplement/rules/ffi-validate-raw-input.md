# ffi-validate-raw-input

> Null-check and UTF-8-validate every incoming pointer before you use it

## Why It Matters

A boundary function is a trust boundary. Everything arriving through it was produced
by code the Rust compiler never checked: the pointer may be null, dangling, or
unaligned, and a `char*` may not be NUL-terminated or valid UTF-8. Dereferencing
without checking converts a caller mistake into undefined behavior inside your
library, where it will be blamed on Rust.

Validation at the boundary is one of the cases where being lazy is wrong: this is
input validation at a trust boundary, and it is never optional.

## Bad

```rust
use std::ffi::CStr;
use std::os::raw::c_char;
use std::path::PathBuf;

#[no_mangle]
pub extern "C" fn wb_open(path: *const c_char) -> bool {
    // Null deref if the caller passes NULL; UB on a non-terminated buffer;
    // panic on invalid UTF-8, which then unwinds across the ABI.
    let path = unsafe { CStr::from_ptr(path) };
    let path = PathBuf::from(path.to_str().unwrap());
    path.exists()
}
```

## Good

```rust
use std::ffi::CStr;
use std::os::raw::c_char;
use std::path::PathBuf;

/// Decodes a caller-provided C string into a path.
///
/// # Safety
///
/// `path` must be null or a valid NUL-terminated string that stays alive and
/// unmodified for the duration of the call.
unsafe fn read_path(path: *const c_char) -> Result<PathBuf, &'static str> {
    if path.is_null() {
        return Err("null path pointer");
    }
    // SAFETY: checked non-null above; the caller contract guarantees NUL
    // termination and that the buffer outlives this call.
    let raw = unsafe { CStr::from_ptr(path) };
    let text = raw.to_str().map_err(|_| "path was not valid UTF-8")?;
    if text.is_empty() {
        return Err("empty path");
    }
    Ok(PathBuf::from(text))
}

#[no_mangle]
pub extern "C" fn wb_open(path: *const c_char) -> bool {
    // SAFETY: read_path performs the null check and only reads within the call.
    match unsafe { read_path(path) } {
        Ok(path) => path.exists(),
        Err(_message) => false, // record via the last-error channel
    }
}
```

## Key Points

- Null is the one invalid pointer you *can* detect. Check it every time; you cannot
  check dangling, so state that requirement in a `# Safety` section instead.
- Use `to_str()` and handle the error. `to_string_lossy()` is acceptable only for
  diagnostic text, never for a path or identifier you will act on.
- Validate lengths and ranges too: an incoming `usize` count from C is untrusted, and
  a bounds check is cheaper than the corruption it prevents.
- Keep the decoding inside the `catch_unwind` shield, since validation itself can
  panic on an unexpected input.

## In This Workspace

`axel-ffi` centralizes this in `read_path`, called inside the `catch_unwind` closure
of each boundary function, mapping failures to `AxelEngineError::EngineInternal` with
a message. The crate also sets `#![allow(clippy::not_unsafe_ptr_arg_deref)]` with a
comment explaining that public entry points take raw pointers by design - that is a
deliberate, documented exception, not a blanket silencing.

## See Also

- [ffi-no-unwind-boundary](ffi-no-unwind-boundary.md) - validation runs inside the shield
- [ffi-error-out-of-band](ffi-error-out-of-band.md) - reporting why validation failed
