# measure-before-optimize

> No new dependency and no codegen lever without a profile that shows the problem

## Why It Matters

The base standard contains rules that read as recommendations but are really
conditional tradeoffs: swap `Vec` for `SmallVec`, `String` for a compact string,
`SipHash` for `ahash`, add `#[inline(always)]`, set `target-cpu=native`, enable PGO.
Applied without measurement they cost real things - a dependency to maintain and
audit, a larger binary, a build that only runs on the machine that produced it -
while the actual bottleneck stays untouched.

An agent applying rules top-down is especially prone to this, because each rule looks
locally reasonable. The gate is evidence, not judgment.

## Bad

```toml
# Added because a rule mentioned them. No benchmark was run.
[dependencies]
smallvec = "1"
ahash = "0.8"
compact_str = "0.8"
```

```rust
// Applied everywhere "for speed"; bloats the binary and can defeat the
// inliner's own heuristics.
#[inline(always)]
fn add(a: u32, b: u32) -> u32 { a + b }
```

## Good

```text
1. Reproduce the slow path in a benchmark (criterion, or a timed integration run).
2. Profile it. Confirm the hot spot is where you think it is.
3. Change one thing.
4. Re-measure against the same benchmark.
5. Record the before/after numbers in the PR description.
```

```rust
// Justified: measured 18% of calculate() time in HashMap hashing with 10k
// cell keys; ahash cut wall time from 240ms to 197ms on the bench fixture.
use ahash::AHashMap;
```

## Rules Gated by This

`mem-smallvec`, `mem-thinvec`, `mem-arrayvec`, `mem-compact-string`, `perf-ahash`,
and every `opt-*` rule: `opt-inline-always-rare`, `opt-inline-small`,
`opt-likely-hint`, `opt-cold-unlikely`, `opt-target-cpu`, `opt-pgo-profile`,
`opt-codegen-units`, `opt-lto-release`, `opt-simd-portable`, `opt-bounds-check`.

`perf-profile-first` in the base standard says the same thing; this rule makes it
binding over the others rather than one voice among thirteen.

## Key Points

- `opt-lto-release` and `opt-codegen-units` are the mildest of the set - build-time
  cost for a usually-real win - but still belong in a measured release-profile change.
- `target-cpu=native` produces artifacts that may not run on other machines. Never
  set it for a distributed build.
- A dependency added for performance must be re-justified if the hot path changes.
  Removing it later is as legitimate as adding it.
- Stdlib first. The base standard's own `anti-premature-optimize` agrees.

## See Also

- [msrv-edition-guard](msrv-edition-guard.md) - the other standing override
