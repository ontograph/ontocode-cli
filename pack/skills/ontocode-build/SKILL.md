---
name: ontocode-build
description: Native build, test, lint, binary and content-pack packaging, release, compiler-lane, artifact-lock, polling, and final-validation rules. Read before forming or running any Cargo, nextest, Just, Bazel, format, package, content-pack, or release command.
---

# Build, Validation, and Release

These rules apply to every command that compiles, tests, lints, packages, or
builds.

- Install required repository commands such as `just`, `rg`, or `cargo-insta`
  when absent.
- Work on the native host only. Limit compiler parallelism to 4 CPUs:
  `CARGO_BUILD_JOBS=4` for Cargo/Just and `--jobs=4` for Bazel.
- Do not build or link user-facing binaries during routine validation. Use
  crate-scoped library checks and tests unless binary startup, packaging,
  release, or end-to-end proof is required.
- For user-facing binary work, build only the release binary with
  `cd ontocode-rs && CARGO_BUILD_JOBS=4 cargo build --release -p ontocode-cli --bin ontocode`.
  Use only `ontocode-rs/target/release`; do not set another target directory or
  copy the artifact elsewhere. Report exact commands, working directory, and
  expected artifact path in the final response.
- Release publication, distribution-target policy, and release documentation are
  owned by `.ontocode/skills/ontocode-release-publish/SKILL.md`. Read it before
  publishing a release, uploading release assets, or publishing release docs.
- Before preparing a release or distribution, run `cargo clean` in
  `ontocode-rs` and other large sub-workspaces.
- Before Cargo, nextest, Just, or Bazel validation, inspect this checkout for
  active `cargo`, `cargo-nextest`, `rustc`, relevant `just`, Bazel processes,
  and artifact locks. Do not start overlapping work. Report the active process
  or `blocked: cargo artifact lock`.
- Never launch a new validation command while another validation command is
  running in the same checkout.
- Stop autonomous polling after three observations with no new output. All
  tools and command shapes share the same budget for one running process. An
  explicit user status request permits one fresh observation, not a new loop.
- Run long compiler work through
  `just compiler-lane-detached <absolute-new-artifact-directory> <command>` only
  when the active manager assigned that exact absent directory. Launcher exit 0
  proves only startup; `result.json` is terminal authority and `output.log`
  contains exact output. Resume from those artifacts after transport failure;
  do not redispatch or create a waiter role.
- After the validation-job pilot has an accepted clean-checkout smoke,
  `just validation-job <path|->` may be used only when per-step lifecycle,
  elapsed time, and exit code are sufficient. Use the ordinary compiler lane
  when exact diagnostics, warnings, snapshots, test names, or counts are needed.
- Treat a transport-level failure such as `Transport closed` as terminal for
  that transport in the current turn. Do not probe or repeat identical calls.
- Run `just fmt` in `ontocode-rs` after code changes anywhere in the repository.

## Agents and Skills Content Pack

When a release distributes agents or skills, build one versioned content pack.
A pack may ship alongside a CLI release or on its own `content-pack-v*` tag,
because agents and skills change far more often than the binary and a
content-only change must not require a full rebuild. Publishing and live
install verification remain owned by
`.ontocode/skills/ontocode-release-publish/SKILL.md`.

1. Export only entries named in the reviewed allowlist at
   `scripts/content_pack_allowlist.toml`, and build the pack with
   `just build-content-pack <version> <staging-dir>`. Never copy complete
   `.agents`, `.ontocode`, `$HOME/.agents`, or `$ONTOCODE_HOME` trees, and do
   not assemble the archive by hand.
2. Stage the public pack with this canonical layout:

   ```text
   content-pack/
   ├── pack.toml
   ├── skills/<name>/SKILL.md
   └── agents/<name>.toml
   ```

   Include each entry's public name, source provenance, license, and version in
   `pack.toml`. Do not export home `.system` skills unless repository ownership
   and redistribution rights are explicit.
3. Reject symlinks, special files, path traversal, duplicate public names,
   built-in agent-name collisions, absolute machine paths, credentials, private
   repository references, internal hostnames, and unreleased planning content.
   Treat every unexplained leak-scan match as blocking. Record an accepted
   match in the allowlist's `[review]` section with the reason it carries no
   location or credential, so the generator fails on anything unreviewed.
   Resolve a duplicate public name by recording the winning source, and record
   every deliberate omission in `exclude` so it stays reviewable.
4. Validate every skill contains exactly one `SKILL.md`. Validate every agent
   with the existing strict standalone-agent parser and require non-empty
   `name`, `description`, and `developer_instructions` fields.
5. Produce immutable release assets named for the pack version:

   ```text
   ontocode-content-pack-<version>.tar.gz
   ontocode-content-pack-<version>.manifest.json
   ```

   The staging pack is also the single input for the browsable `pack/` mirror in
   the distribution repository; see
   `.ontocode/skills/ontocode-release-publish/SKILL.md`. Do not create a second
   assembly path for that mirror.

   The JSON manifest must record every archive path, byte size, SHA-256 digest,
   provenance, license, and destination class. Add both files to the release
   staging directory and cover them with the release `SHA256SUMS`. The archive
   must rebuild byte-for-byte from the same source commit; pin both the entry
   metadata and the gzip timestamp, since gzip otherwise records the build
   time and breaks reproducibility.
6. Validate installation in temporary home and project roots before publishing.
   Home destinations are `$ONTOCODE_HOME/skills/<name>` and
   `$ONTOCODE_HOME/agents/<name>.toml`; project destinations are
   `<repo>/.agents/skills/<name>` and `<repo>/.ontocode/agents/<name>.toml`.
   Refuse overwrites by default. A forced update must back up the existing file,
   and uninstall may remove only unchanged files owned by the recorded manifest.
7. Hand the staged archive, manifest, installer, and validation evidence to the
   release-publication workflow. Do not upload or copy them to another public
   repository.

## Validation Tiers

1. Do not run `cargo test` directly; use repository `just` commands.
2. For Markdown, TOML, prompt, plan, or tracking-only changes, run the relevant
   parser/checker, `just validate-coder-contract` for coder/global prompt changes,
   and `git diff --check`. Do not compile Rust unless the DoD requires it.
   Coder role files under `.ontocode/agents/*.toml`, including the `cdr-*`
   mirrors, are tier-2 work: `just validate-coder-contract` is their complete
   gate and runs in well under a second. Do not start the compiler lane for a
   role-file-only change.
3. During Rust edit loops, run
   `CARGO_BUILD_JOBS=4 just check-fast -p <crate> --lib` after a coherent batch.
4. At a behavioral checkpoint, run
   `CARGO_BUILD_JOBS=4 just test-fast -p <crate> --lib <filter>`. Reuse an assigned
   `ONTOCODE_ITER_TARGET_DIR` serially and never start concurrent writers.
5. Use `just test -p <crate> -- <filter>` only for assigned integration or
   pre-merge gates. Ask before a complete workspace test. Avoid `--all-features`
   for routine validation.

For a crate-local library change, finish with
`CARGO_BUILD_JOBS=4 cargo clippy --fix --lib --allow-dirty -p <crate>`. For a
large change affecting integration tests, binaries, or shared behavior, use
`CARGO_BUILD_JOBS=4 just fix -p <project>`. Use workspace-wide `just fix` only
when shared-crate impact requires it. Do not rerun tests after `fix` or `fmt`.
Run `just fmt` after the final validation command, never before it. Formatting
rewrites file mtimes, so a preceding `fmt` forces a full crate rebuild on the
next lane command and discards otherwise-warm Cargo state.

## Compiler Cache Fingerprints

Cargo fingerprints include `RUSTFLAGS`, so changing linker or codegen flags
builds into a separate cache slot instead of reusing the default one. Measured
on this repository, adding `-C link-arg=-fuse-ld=mold` to the iteration lane
recompiled 885 crates in 248s versus 3 crates in 32s on the default path, and
left both variants resident on disk. Keep routine `check-fast` and `test-fast`
runs on default flags. Use `just test-fast-mold` only for a deliberate
link-heavy experiment, and expect the first run after any flag switch to pay a
full workspace rebuild.

`RUSTC_WRAPPER` changes the same fingerprint. When `sccache` is installed, opt
in for a session by exporting `RUSTC_WRAPPER=sccache` before the lane command;
the first run after enabling or disabling it rebuilds the workspace, so switch
it per working session rather than per command. It caches rustc invocations
across flag switches and branch changes, but cannot serve a crate whose own
source changed, which is the common single-crate iteration case here. Check
`sccache --show-stats` for the hit rate before assuming it helped.
