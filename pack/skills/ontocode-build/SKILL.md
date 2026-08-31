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
  owned by `$ONTOCODE_HOME/skills/ontocode-release-publish/SKILL.md`. Read it before
  publishing a release, uploading release assets, or publishing release docs.

## Release Staging Cleanup

Every release run must own one disposable staging directory and remove it at
every terminal outcome, including successful publication, validation failure,
interruption, and cancellation.

- Create a new dedicated directory for the current run. Record its canonical
  absolute path before writing any asset and install cleanup immediately.
- Never adopt a pre-existing directory. Create a marker file inside the new
  directory that identifies it as staging owned by the current run.
- Cleanup may recursively remove only the recorded directory after confirming
  that it is a non-symlink directory owned by the current user, contains the
  current run's marker, is not a Git repository, and is not registered by
  `git worktree list --porcelain`.
- Never delete by glob, prefix sweep, unresolved variable, or relative path.
  In particular, do not run recursive deletion against `ontocode-release-*`.
- Delete the owned staging directory after the final release upload and smoke
  checks. On failure, copy any small diagnostic evidence that must survive into
  the normal artifact or log location first, then delete the staging directory.
- Treat alternate checkout paths as aliases when they resolve to the same
  canonical path. Cleanup the canonical target once; do not create duplicate
  release staging trees through multiple spellings.
- This rule applies only to disposable release staging. Preserve distribution
  clones, Git worktrees, pre-existing directories, and any directory whose
  ownership checks fail; report `blocked: unsafe release staging cleanup`
  instead of deleting it.
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
  `just compiler-lane-detached <unique-job-name> <command>` only when the active
  manager assigned that exact absent direct-child job name. Receipts live under
  `$ONTOCODE_COMPILER_ARTIFACT_ROOT`, or
  `$ONTOCODE_HOME/artifacts/compiler-lane/` when the override is unset, with
  `~/.ontocode` as the `ONTOCODE_HOME` fallback. Launcher exit 0 proves only
  startup; `result.json` is terminal authority and `output.log` contains exact
  output. Every receipt also contains ownership metadata in `artifact.json`.
  The launcher never automatically deletes or moves existing receipts. Cleanup
  is an explicit owner-reviewed operation outside the launch path. Set
  `ONTOCODE_COMPILER_ARTIFACT_RETENTION=retain` for an explicitly retained job,
  which records that intent in `artifact.json` for future operator cleanup.
  Existing absolute artifact directories remain accepted for active legacy
  plans and are marked external. After transport failure, resume by harvesting
  the existing job with `just lane-result <job-name>`; do not redispatch or
  create a waiter role.
- After the validation-job pilot has an accepted clean-checkout smoke,
  `just validation-job <path|->` may be used only when per-step lifecycle,
  elapsed time, and exit code are sufficient. Use the ordinary compiler lane
  when exact diagnostics, warnings, snapshots, test names, or counts are needed.
- Treat a transport-level failure such as `Transport closed` as terminal for
  that transport in the current turn. Do not probe or repeat identical calls.
- Run `just fmt` in `ontocode-rs` after code changes anywhere in the repository.

## Long-Running Commands

Builds and test suites outlive a foreground call. Detach them, then read a
result; never burn wall clock waiting in the shell.

Never poll with `sleep`. A `sleep 25` loop around a status check spends real
time to learn nothing: the command is not faster for being watched, and each
iteration costs a turn. Measured sessions have lost hundreds of minutes this
way. Use the status action, which answers immediately.

For a compiler-lane job, `just lane-result <job-name>` is the canonical
terminal receipt reader once the job name is known. It validates the managed
metadata and terminal result and is the evidence source for exit status and
bounded output. Do not substitute `lane-status`, generic background status, or
direct `result.json`/`output.log` reads as the normal harvest path. Use direct
receipt files only when `lane-result` explicitly cannot read or validate the
receipt; report that failure and do not relaunch the job.

Order of preference:

1. `just compiler-lane-detached <unique-job-name> <command>` for compiler work
   the active manager has assigned. Receipts survive transport failure, so
   resume with `just lane-result <job-name>` rather than relaunching.
2. `just lane-result <job-name>` for a deterministic, read-only receipt harvest.
   It validates the managed artifact metadata and terminal `result.json`, then
   returns the exit code, elapsed time, and a bounded `output.log` tail. It never
   launches, changes, or deletes a job. Use it once the receipt exists; an
   incomplete receipt is a terminal evidence failure, not a reason to relaunch.
3. `run_in_background: true` on `ctx_shell` for other long commands. Keep the
   returned `job_id` and harvest with `background_action: "status"`.

Harvest or cancel every job you start. A started job whose result is never read
is wasted compute and an unproven claim; if it is no longer needed, cancel it
with `background_action: "cancel"` rather than abandoning it. Do not launch a
replacement for a job you have not harvested.

`nohup`, `&`, and hand-rolled PID files reproduce the detached lane without its
receipts, ownership metadata, or artifact-lock checks. Prefer the lane; it
already solves the problem.

The three-observation polling cap above still applies to status checks. When a
job needs longer, say so and move to disjoint work instead of watching it.

## Agents and Skills Content Pack

When a release distributes agents or skills, build one versioned content pack.
A pack may ship alongside a CLI release or on its own `content-pack-v*` tag,
because agents and skills change far more often than the binary and a
content-only change must not require a full rebuild. Publishing and live
install verification remain owned by
`$ONTOCODE_HOME/skills/ontocode-release-publish/SKILL.md`.

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
   `$ONTOCODE_HOME/skills/ontocode-release-publish/SKILL.md`. Do not create a second
   assembly path for that mirror.

   The JSON manifest must record every archive path, byte size, SHA-256 digest,
   provenance, license, and destination class. Add both files to the release
   staging directory and cover them with the release `SHA256SUMS`. The archive
   must rebuild byte-for-byte from the same source commit; pin both the entry
   metadata and the gzip timestamp, since gzip otherwise records the build
   time and breaks reproducibility.
6. Validate installation in a temporary home root before publishing.
   Definitions install only to `$ONTOCODE_HOME/skills/<name>` and
   `$ONTOCODE_HOME/agents/<name>.toml`.
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
   Coder role files under `$ONTOCODE_HOME/agents/*.toml`, including the `cdr-*`
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
