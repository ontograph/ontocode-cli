# Qualify Rust Artifact Provenance

A checksum identifies bytes. It does not by itself prove source lineage,
freshness, toolchain identity, or a repeatable build.

## Required Checks

- Record the artifact path, size, SHA-256, mtime, inode, and hardlink count with
  the source revision and worktree identity used to produce it.
- For static archives, inspect member metadata as well as the archive digest;
  zeroed member timestamps do not remove the need for build-input evidence.
- Treat hardlink uplift as an observation, not proof of determinism. Copy the
  artifact when later steps must be isolated from Cargo's target cache.
- Prove all relevant Rust sources, manifests, `Cargo.lock`, `build.rs`, flags,
  toolchain, and native consumers are covered by the recorded build graph.
- Call output deterministic only after at least two independently produced
  artifacts have the required identical bytes, or scope the claim explicitly to
  one observed artifact.

Use `cargo-native-verification` for freshness and use
`axel-release-qualification` for publication-grade source lineage.
