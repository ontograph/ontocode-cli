# supply-semver-checks

> Run `cargo-semver-checks` before publishing a library version bump

## Why It Matters

SemVer breakage in Rust is easy to cause and hard to see in review. Removing a trait
impl, adding a field to a public struct that was constructible with a literal,
narrowing a bound, or making a public enum non-exhaustive all break downstream code
without touching an obvious signature. The compiler cannot warn you because, from the
crate's own perspective, nothing is wrong.

`cargo-semver-checks` compares the public API against the published version and
reports the required bump. It removes the guesswork from choosing patch vs minor vs
major.

## Bad

```text
Version bumped by hand based on how large the diff felt.
A public struct gained a field in a "patch" release; every downstream crate
that constructed it with a struct literal fails to compile.
```

## Good

```bash
cargo install cargo-semver-checks --locked
cargo semver-checks check-release --package axel-core
```

```yaml
# CI, on any PR touching a published crate
- run: cargo semver-checks check-release
  working-directory: rust
```

## Key Points

- The base standard's `api-non-exhaustive` prevents part of this class up front; add
  `#[non_exhaustive]` before the first release, not after.
- Internal-only crates do not need this gate. Apply it to anything published or
  consumed across a repository boundary.
- The tool reports the minimum required bump; it does not decide policy for
  pre-1.0 crates, where a minor bump is already allowed to break.
- Run it before tagging, not after. A published version cannot be corrected.

## In This Workspace

`axel-core`, `axel-xlsx`, and `axel-ffi` are path dependencies at `0.1.0` and are not
published, so this gate is not required today. It becomes required the first time one
of them is consumed outside this repository.

## See Also

- [supply-cargo-deny](supply-cargo-deny.md) - dependency policy enforcement
