# msrv-edition-guard

> Verify every suggested API against edition 2021 and Rust 1.70 before you write it

## Why It Matters

The base `axel-rust-standard` targets Rust 1.96 and edition 2024. This workspace
pins `edition = "2021"` and `rust-version = "1.70"` in `rust/Cargo.toml`. Following a
base rule verbatim can therefore produce code that does not compile here, or that
compiles on a developer's newer toolchain and breaks the MSRV build later - the worse
failure, because it lands in main.

Silently raising the MSRV is a compatibility decision disguised as a code change.

## Bad

```rust
// Edition 2024 syntax from the base standard's unsafe rules. Does not compile
// under edition 2021.
unsafe extern "C" {
    safe fn probe() -> u32;
}

// Also edition 2024 only:
// #[unsafe(no_mangle)]
// pub extern "C" fn entry() {}
```

## Good

```rust
// Edition 2021 form: bare extern block, bare attribute.
extern "C" {
    fn probe() -> u32;
}

#[no_mangle]
pub extern "C" fn entry() -> u32 {
    // SAFETY: probe has no preconditions beyond being linked, which the build
    // guarantees.
    unsafe { probe() }
}
```

## Out of Scope at This MSRV

| Base-standard advice | Why it does not apply |
|---|---|
| `unsafe extern {}` blocks, `safe` items | edition 2024 |
| `#[unsafe(no_mangle)]`, `#[unsafe(export_name)]` | edition 2024 |
| native `async fn` in traits (`async-fn-in-trait`) | stable 1.75, above MSRV 1.70 |
| `AsyncFn`/`AsyncFnMut` bounds (`async-async-fn-bounds`) | above MSRV |
| `let`-chains in `if let` (`pat-if-let-chains`) | edition 2024 |
| `gen` blocks | edition 2024 |

Use `Pin<Box<dyn Future>>` where the base standard suggests `async fn` in traits; see
[pin-self-referential](pin-self-referential.md).

## Key Points

- Check the "stable since" note on any std API a rule cites before adopting it.
- Keep `rust-version` accurate. It is what makes a too-new API a build error instead
  of a mystery.
- Raising the MSRV or the edition is a deliberate, reviewed change with its own
  migration - never a side effect of applying a style rule.
- Verify with the MSRV toolchain, not just the local default, before claiming a rule
  applies.

## See Also

- [measure-before-optimize](measure-before-optimize.md) - the other standing override
