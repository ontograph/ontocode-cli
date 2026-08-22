# pin-no-move-out

> Never move a value out of a `Pin<&mut T>` unless `T: Unpin`

## Why It Matters

Pinning is a promise, and the unsafe API lets you break it. `mem::replace`,
`mem::swap`, and `Pin::get_unchecked_mut` all move or expose the pinned value; doing
that to a self-referential type leaves its internal pointers aimed at freed or reused
memory. The compiler stops the safe paths, so the breakage only happens where someone
reached for `unsafe` to quiet an error.

The safe API is deliberately narrow: `as_mut`, `as_ref`, and the projections a
library gives you. If you need more, you need a different design, not an
`unsafe` block.

## Bad

```rust
use std::pin::Pin;

struct Machine {
    buffer: String,
    // conceptually points into `buffer`; moving Machine invalidates it
}

fn reset(mut machine: Pin<&mut Machine>) {
    // SAFETY comment would be a lie: this hands out a &mut that allows moving
    // the pinned value, breaking the pin guarantee for a self-referential type.
    let inner = unsafe { machine.as_mut().get_unchecked_mut() };
    let _old = std::mem::replace(inner, Machine { buffer: String::new() });
}
```

## Good

```rust
use std::pin::Pin;

struct Machine {
    buffer: String,
}

// Mutate in place through the pin; never move the whole value.
fn reset(mut machine: Pin<&mut Machine>) {
    // SAFETY: we only mutate a field that is not part of any self-reference and
    // never move the pinned value itself.
    let inner = unsafe { machine.as_mut().get_unchecked_mut() };
    inner.buffer.clear();
}

// Better: if the type is genuinely movable, say so and drop the unsafe entirely.
struct Plain {
    buffer: String,
}

fn reset_plain(mut plain: Pin<&mut Plain>)
where
    Plain: Unpin,
{
    plain.as_mut().get_mut().buffer.clear(); // safe: Unpin permits it
}
```

## Key Points

- `Pin::get_mut` is the safe accessor and requires `T: Unpin`. If it does not compile,
  the type is not movable and `get_unchecked_mut` is not the fix.
- Prefer a pin-projection crate over hand-written `unsafe` projections when a struct
  has a mix of pinned and unpinned fields.
- Every remaining `unsafe` here needs a `// SAFETY:` comment that names the invariant,
  per the base standard's `unsafe-safety-comment`.
- Run `cargo miri test` over code that hand-projects pins; Miri catches the
  use-after-move that ordinary tests miss.

## See Also

- [pin-self-referential](pin-self-referential.md) - getting a correctly pinned value in the first place
