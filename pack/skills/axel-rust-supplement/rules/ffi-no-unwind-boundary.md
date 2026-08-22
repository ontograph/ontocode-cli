# ffi-no-unwind-boundary

> Wrap every `extern "C"` function body in `catch_unwind`; unwinding across the boundary is undefined behavior

## Why It Matters

A Rust panic that propagates out of an `extern "C"` function into C or C++ is
undefined behavior. It is not a clean crash you can debug: the foreign frames were
never compiled with Rust's unwind tables, so the unwinder walks stack it does not
understand. Since Rust 1.81 the compiler inserts an abort at the boundary for
`extern "C"`, which turns UB into a process kill, but that still takes down the host
application with no diagnostic. A boundary function must convert every panic into a
value the caller can branch on.

`AssertUnwindSafe` is normally a smell, but it is the correct tool here: the closure
borrows local state that cannot outlive the call, and you are already committing to
discarding partial work on the panic path.

## Bad

```rust
use std::os::raw::c_char;

pub struct Handle {
    rows: Vec<u32>,
}

// A panic anywhere in here - a slice index, an unwrap, an allocation failure -
// crosses into C. UB, or an abort that kills the host process.
#[no_mangle]
pub extern "C" fn wb_row_at(handle: *mut Handle, index: usize) -> u32 {
    let handle = unsafe { &mut *handle };
    handle.rows[index] // panics on out-of-range
}
```

## Good

```rust
use std::panic::{catch_unwind, AssertUnwindSafe};

pub struct Handle {
    rows: Vec<u32>,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub enum EngineError {
    Ok = 0,
    OutOfRange = 1,
    Internal = 2,
}

// Every failure, including a panic, becomes a status the caller can branch on.
#[no_mangle]
pub extern "C" fn wb_row_at(handle: *mut Handle, index: usize, out: *mut u32) -> EngineError {
    if handle.is_null() || out.is_null() {
        return EngineError::Internal;
    }
    match catch_unwind(AssertUnwindSafe(|| {
        let handle = unsafe { &mut *handle };
        handle.rows.get(index).copied().ok_or(EngineError::OutOfRange)
    })) {
        Ok(Ok(value)) => {
            unsafe { *out = value };
            EngineError::Ok
        }
        Ok(Err(code)) => code,
        // The panic stopped here. Record it, report it, do not let it unwind.
        Err(_) => EngineError::Internal,
    }
}
```

## Key Points

- The `catch_unwind` must wrap the *whole* body, including argument decoding. A
  panic while validating a path is still a panic at the boundary.
- Prefer returning `Result` inside the closure and flattening the
  `Ok(Ok(..)) / Ok(Err(..)) / Err(..)` triple, so expected failures and panics stay
  distinguishable.
- Never swallow the panic silently. Store a message and a stable code in a
  last-error channel so the caller can report something better than "internal".
- `extern "C-unwind"` exists for the rare case where unwinding *should* cross into
  C++ that knows how to receive it. That is not this workspace's contract; do not
  reach for it to avoid writing a shield.

## In This Workspace

`rust/crates/axel-ffi/src/lib.rs` follows this pattern: `axel_workbook_open` wraps
its body in `catch_unwind(AssertUnwindSafe(...))`, maps expected failures to
`AxelEngineError`, and on `Err(_)` sets `"Rust panic at workbook ABI boundary"`
before returning a null pointer. New boundary functions must match it.

## See Also

- [ffi-abort-profile-conflict](ffi-abort-profile-conflict.md) - `panic = "abort"` disables this shield
- [ffi-error-out-of-band](ffi-error-out-of-band.md) - where the panic message goes
