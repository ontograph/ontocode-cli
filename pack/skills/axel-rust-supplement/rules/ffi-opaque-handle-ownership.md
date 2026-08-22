# ffi-opaque-handle-ownership

> Pair every `Box::into_raw` with exactly one `Box::from_raw` free function, and document who owns what

## Why It Matters

Rust state that is too complex for a `#[repr(C)]` struct crosses the boundary as an
opaque pointer. The moment you call `Box::into_raw`, the value leaves Rust's
ownership tracking: nothing will free it, nothing prevents a second free, and nothing
stops the caller from using it after close. The only defense is an explicit,
documented contract with exactly one constructor and one destructor per handle type.

Handing out a pointer without shipping the matching free function is a leak by
construction. Freeing in more than one place is a double-free waiting for a retry
path.

## Bad

```rust
pub struct Workbook {
    sheets: Vec<String>,
}

#[no_mangle]
pub extern "C" fn wb_open() -> *mut Workbook {
    Box::into_raw(Box::new(Workbook { sheets: Vec::new() }))
}

// No free function: every open leaks the whole workbook.
// Worse, some call sites "clean up" by freeing the pointer with libc free(),
// which does not run Drop and corrupts the allocator.
```

## Good

```rust
pub struct Workbook {
    sheets: Vec<String>,
}

/// Creates a workbook handle.
///
/// Ownership transfers to the caller. The handle must be released with exactly one
/// call to `wb_close` and must not be used afterwards.
#[no_mangle]
pub extern "C" fn wb_open() -> *mut Workbook {
    Box::into_raw(Box::new(Workbook { sheets: Vec::new() }))
}

/// Releases a handle returned by `wb_open`.
///
/// Null is accepted and ignored. Passing a pointer twice, or a pointer not
/// produced by `wb_open`, is undefined behavior.
#[no_mangle]
pub extern "C" fn wb_close(handle: *mut Workbook) {
    if handle.is_null() {
        return;
    }
    // SAFETY: the caller contract guarantees this pointer came from wb_open and
    // has not been closed. Reconstructing the Box runs Drop exactly once.
    drop(unsafe { Box::from_raw(handle) });
}
```

## Key Points

- Accept null in the destructor and make it a no-op. It removes an entire class of
  caller-side branching bugs.
- Borrow, do not consume, in ordinary accessors: build `&mut *handle` for the call's
  duration and never `Box::from_raw` outside the destructor.
- Buffers handed to C need the same treatment: if you return a pointer plus length,
  ship the matching release function and state which allocator owns it.
- Document the contract in the doc comment, not just the header. The next person to
  add a retry path reads the Rust side.

## In This Workspace

`axel-ffi` returns `*mut AxelWorkbookHandle` from `axel_workbook_open` via
`Box::into_raw` and releases it in `axel_workbook_close`. `AxelByteBuffer` follows
the same one-owner discipline. Any new handle type must arrive with its destructor in
the same change.

## See Also

- [ffi-validate-raw-input](ffi-validate-raw-input.md) - checking pointers on the way in
- [ffi-repr-c-layout](ffi-repr-c-layout.md) - when a value type is enough
