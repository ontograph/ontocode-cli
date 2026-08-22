# Compare Against a Fresh Sealed Oracle

Oracle parity is meaningful only when both sides come from identified inputs and
a current build lane.

## Required Checks

- Record the sealed corpus and golden-file paths, byte counts, SHA-256 hashes,
  producing tool or oracle version, and command used to seal them.
- Build the Rust artifact and native consumer in one declared lane; do not mix
  stale outputs from another worktree or target directory.
- Refuse stale-target/mtime conflicts. Never repair them with `touch`; rebuild
  through the owning recipe.
- Run the exact parity command, capture its exit status and structured output,
  and state whether it compares values, formulas, packages, or rendered behavior.
- Route engine-readiness and rollback decisions to `axel-rust-engine-seam-audit`;
  publication claims additionally belong to `axel-release-qualification`.
