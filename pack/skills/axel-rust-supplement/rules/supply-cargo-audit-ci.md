# supply-cargo-audit-ci

> Fail CI on known RUSTSEC advisories instead of discovering them at release time

## Why It Matters

A vulnerable transitive dependency is invisible during normal development. `cargo
audit` checks `Cargo.lock` against the RUSTSEC database, so it catches the case that
matters most: a crate you never chose, pulled in three levels down, with a published
advisory. Running it only before a release means the fix lands under deadline
pressure, often alongside an unrelated version bump.

A scheduled run matters as much as the per-PR run: advisories are published against
code you already shipped, so a green build today says nothing about tomorrow.

## Bad

```text
cargo audit run manually, occasionally, by one person.
Cargo.lock is committed but nothing checks it, so an advisory against a
transitive dependency can sit unnoticed for months.
```

## Good

```yaml
# .github/workflows/rust-audit.yml
name: rust-audit
on:
  push:
    paths: ["rust/**"]
  pull_request:
    paths: ["rust/**"]
  schedule:
    - cron: "0 6 * * 1"   # catches advisories published after the code merged

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cargo install cargo-audit --locked
      - run: cargo audit --deny warnings
        working-directory: rust
```

## Key Points

- Commit `Cargo.lock` for the workspace. `cargo audit` reads the lockfile; without it
  there is nothing precise to check.
- Use `--deny warnings` so unmaintained-crate notices are visible rather than
  scrolled past.
- When an advisory has no fixed version yet, record the accepted risk with an
  `ignore` entry and an expiry date. An unexplained permanent ignore is how audits die.
- Pair with `cargo update` discipline: an audit that always fails teaches the team to
  ignore it.

## In This Workspace

`rust/Cargo.lock` is committed, so the audit has a precise target. No audit workflow
is wired up yet.

## See Also

- [supply-cargo-deny](supply-cargo-deny.md) - licenses, bans, and sources
