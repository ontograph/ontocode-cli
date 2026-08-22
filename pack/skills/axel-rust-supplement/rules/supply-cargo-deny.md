# supply-cargo-deny

> Gate licenses, duplicate versions, and advisories with `cargo-deny` in CI

## Why It Matters

Dependencies arrive with obligations: incompatible licenses, unmaintained crates,
multiple versions of the same library bloating the binary, and sources nobody vetted.
Reviewing that by hand does not scale past a handful of direct dependencies, and
transitive additions never get reviewed at all. `cargo-deny` turns the policy into a
file the build enforces.

For a project shipping under a specific license, the license check alone justifies
the setup: a copyleft transitive dependency discovered at release time is expensive.

## Bad

```text
No deny.toml anywhere in the workspace.
License compatibility is "checked" by whoever remembers to look at a new crate,
duplicate versions accumulate silently, and RUSTSEC advisories surface only when
someone happens to run cargo audit locally.
```

## Good

```toml
# deny.toml at the workspace root
[advisories]
yanked = "deny"

[licenses]
# Allowlist must match what the project can actually ship.
allow = ["MPL-2.0", "MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "Unicode-3.0"]
confidence-threshold = 0.9

[bans]
multiple-versions = "warn"   # tighten to "deny" once the tree is clean
wildcards = "deny"

[sources]
unknown-registry = "deny"
unknown-git = "deny"
```

```yaml
# CI step
- name: cargo-deny
  uses: EmbarkStudios/cargo-deny-action@v2
  with:
    manifest-path: rust/Cargo.toml
```

## Key Points

- Start `multiple-versions = "warn"`. Setting it to `deny` on an existing tree
  produces noise that gets suppressed wholesale, defeating the point.
- The license allowlist must reflect the shipping license, not a generic list. This
  workspace's crates are MPL-2.0.
- Keep `deny.toml` in review scope: a change to the allowlist is a licensing decision.
- `cargo-deny` covers advisories too, but a dedicated audit step gives a clearer
  failure signal; see the companion rule.

## In This Workspace

No `deny.toml` exists under `rust/`. The workspace declares `license = "MPL-2.0"` in
`[workspace.package]`, so an allowlist is straightforward to write and worth adding
before the dependency tree grows further.

## See Also

- [supply-cargo-audit-ci](supply-cargo-audit-ci.md) - the advisory half of this
