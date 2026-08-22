# ffi-error-out-of-band

> Return a stable status code; carry the human-readable detail in a separate last-error channel

## Why It Matters

`Result<T, E>` has no C representation, so the boundary must split it: a machine
value the caller branches on, and a message a human reads. Collapsing both into one
channel forces callers to parse prose, which breaks the moment you improve the
wording. A bare `bool` is worse still - it tells the host that something failed but
not whether to retry, fall back, or surface a permission error.

A stable numeric code is an API contract. Treat renumbering it as a breaking change.

## Bad

```rust
use std::os::raw::c_char;

// The caller can only distinguish "worked" from "did not work", and any
// recovery logic ends up string-matching a message that is free to change.
#[no_mangle]
pub extern "C" fn wb_open(path: *const c_char) -> bool {
    false
}
```

## Good

```rust
use std::cell::{Cell, RefCell};
use std::ffi::CString;
use std::os::raw::c_char;

#[repr(i32)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum EngineError {
    Ok = 0,
    NotFound = 1,
    CapabilityUnavailable = 2,
    Internal = 3,
}

thread_local! {
    static LAST_ERROR: RefCell<CString> = RefCell::new(CString::default());
    static LAST_ERROR_CODE: Cell<EngineError> = Cell::new(EngineError::Ok);
}

fn set_last_error(code: EngineError, message: &str) {
    LAST_ERROR_CODE.with(|slot| slot.set(code));
    LAST_ERROR.with(|slot| {
        *slot.borrow_mut() = CString::new(message).unwrap_or_default();
    });
}

/// Returns the message for the most recent failure on this thread.
///
/// The pointer stays valid until the next call that sets an error on the same
/// thread. Callers must copy it before making another engine call.
#[no_mangle]
pub extern "C" fn wb_last_error() -> *const c_char {
    LAST_ERROR.with(|slot| slot.borrow().as_ptr())
}

#[no_mangle]
pub extern "C" fn wb_last_error_code() -> EngineError {
    LAST_ERROR_CODE.with(|slot| slot.get())
}
```

## Key Points

- Make the error channel thread-local. A global last-error is a data race the moment
  the host calls from two threads.
- Clear the previous error at the start of each entry point so a stale message cannot
  be attributed to a later success.
- Document the lifetime of the returned string pointer. "Valid until the next call on
  this thread" is a contract the caller can honor; silence is not.
- Distinguish expected failures from panics in the code space, so the host can tell a
  missing file from an engine bug.

## In This Workspace

`axel-ffi` implements exactly this shape: `AxelEngineError` as the stable code,
`axel_last_error` / `axel_last_error_code` as thread-local accessors, `clear_last_error`
at entry, and `set_last_failure` on the expected-error path. The panic path sets
`EngineInternal` with `"Rust panic at workbook ABI boundary"`, keeping bugs
distinguishable from ordinary failures.

## See Also

- [ffi-no-unwind-boundary](ffi-no-unwind-boundary.md) - the panic path feeds this channel
