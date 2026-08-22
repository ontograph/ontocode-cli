# pin-self-referential

> Use `Box::pin` when a future or struct holds a pointer into itself

## Why It Matters

Most Rust values can be moved freely, and the compiler assumes it. A self-referential
value breaks that assumption: it stores a pointer to its own field, so moving it
leaves the pointer aimed at the old address. `Pin` is the type-level promise that a
value will not move again, which is why every `async fn` body compiles to a
self-referential state machine that must be pinned before it can be polled.

You meet this in practice through error messages, not theory: storing a future in a
struct, returning a boxed future from a trait method, or holding a stream across
calls all require a pinned pointer.

## Bad

```rust
use std::future::Future;

// A bare `dyn Future` cannot be polled: poll() needs Pin<&mut Self>, and the
// state machine may be self-referential, so this does not compile.
pub struct Task {
    work: Box<dyn Future<Output = u32> + Send>,
}
```

## Good

```rust
use std::future::Future;
use std::pin::Pin;

// Box::pin gives a stable heap address and satisfies poll()'s Pin<&mut Self>.
pub struct Task {
    work: Pin<Box<dyn Future<Output = u32> + Send>>,
}

impl Task {
    pub fn new(work: impl Future<Output = u32> + Send + 'static) -> Self {
        Self { work: Box::pin(work) }
    }
}

// The same shape lets a trait return a future without native async fn in traits,
// which is the portable form on editions before 2024 / older MSRVs.
pub trait Engine {
    fn calculate(&self) -> Pin<Box<dyn Future<Output = u32> + Send + '_>>;
}
```

## Key Points

- `Box::pin` is the default answer. Reach for `std::pin::pin!` (stack pinning) only
  when the value never leaves the current scope and the allocation actually matters.
- A type that is `Unpin` can be moved even while pinned; most ordinary data is
  `Unpin`, which is why you rarely see `Pin` outside async code.
- If you find yourself writing `unsafe { Pin::new_unchecked(..) }`, stop and use
  `Box::pin`. The unchecked constructor asserts an invariant the compiler cannot see,
  and getting it wrong is UB.
- `Pin<Box<dyn Future>>` is the standard way to store or return heterogeneous futures
  on Rust 1.70, where native `async fn` in traits is unavailable.

## See Also

- [pin-no-move-out](pin-no-move-out.md) - what pinning forbids afterwards
- [msrv-edition-guard](msrv-edition-guard.md) - why `async fn` in traits is out of scope here
