# Changelog

Full release notes and downloadable assets are published on the
[Ontocode releases page](https://github.com/ontograph/ontocode-cli/releases).
Per-release notes are also kept under [docs/releases](docs/releases).

## Content Pack v4 — `content-pack-v4`

Standalone curated agents and skills update published independently of the CLI
binary.

- publishes 25 agent definitions and 27 skills from the reviewed exact allowlist
- records archive paths, provenance, licenses, sizes, and SHA-256 digests
- updates the browsable `pack/` mirror from the same archive
- keeps non-overwriting home and project-local installation behavior

See the [Content Pack v4 release](https://github.com/ontograph/ontocode-cli/releases/tag/content-pack-v4).

## 0.4.2.5 — `rust-v0.4.2.5`

Internal development fix release built from the reviewed August 23, 2026
source snapshot. Cargo package version `0.4.2+5`.

- prevents assistant-prefill requests from reaching provider request paths
- aligns bounded sub-agent spawn selection with the current configuration APIs
- preserves active-task selection for concurrent worktree validation flows
- makes the default CLI installer select the newest CLI release even when a
  newer content-pack release exists
- hardens detached compiler receipt ownership, path validation, and retention
- publishes the matching curated agents and skills pack without changing the
  independently versioned Content Pack v3 release

See [docs/releases/v0.4.2.5.md](docs/releases/v0.4.2.5.md).

## Content Pack v1 — `content-pack-v1`

First content pack released independently of the CLI binary, so agents and
skills can be updated without reinstalling or rebuilding the CLI.

- publishes 27 agent definitions and 47 skills built from a reviewed allowlist
- adds a manifest recording every archive path, byte size, and SHA-256 digest
- installs to `$ONTOCODE_HOME` or a named project, refusing to overwrite an
  existing skill or agent
- content-pack installer now resolves `content-pack-*` tags and selects the
  newest content pack when `--release` is omitted

## 0.4.2.4 — `rust-v0.4.2.4`

Internal development prerelease built from the complete authorized development
checkpoint on August 19, 2026. Cargo package version `0.4.2+4`.

- includes current manager-loop recovery and role-routing fixes
- includes session diagnostics, Excel offline tooling, and workspace skill
  activation updates from the development checkpoint
- publishes repository-owned build and release-publication skills as an
  optional curated content pack
- preserves the public distribution boundary: only scrubbed release artifacts
  and consumer documentation are published here

See [docs/releases/v0.4.2.4.md](docs/releases/v0.4.2.4.md).

## 0.4.2.3 — `rust-v0.4.2.3`

Internal development release built from the current committed source on August
18, 2026. Cargo package version `0.4.2+3`.

- includes the manager-loop retry fixes published in `0.4.2.2`
- excludes unrelated uncommitted changes from the primary development checkout
- publishes repository-owned build and release-publication skills as an
  optional curated content pack
- supports non-overwriting home and trusted project-local content-pack installs

See [docs/releases/v0.4.2.3.md](docs/releases/v0.4.2.3.md).

## 0.4.2.2 — `rust-v0.4.2.2`

Internal fix release that restores authorized manager-loop retry overrides
after a task has reached its normal attempt cap. Cargo package version
`0.4.2+2`.

- honors an active, authorized task-local model override even when the task's
  ordinary attempt count is exhausted
- preserves the attempt-cap stop for tasks without an override
- preserves the consumed-override stop so a single-use authorization cannot be
  reused
- defaults release installation and documentation to the public distribution
  repository `ontograph/ontocode-cli`

See [docs/releases/v0.4.2.2.md](docs/releases/v0.4.2.2.md).

## 0.4.2.1 — `rust-v0.4.2.1`

Internal development release candidate that restores progress through
manager-loop model routing failures. Cargo package version `0.4.2+1`.

- treats a model-specific unsupported reasoning-effort rejection as a retryable
  manager-loop route failure
- preserves the requested reasoning effort while advancing to the next approved
  model candidate
- keeps service-tier, provider, prompt, capability, permission, and policy
  failures terminal

See [docs/releases/v0.4.2.1.md](docs/releases/v0.4.2.1.md).

## 0.4.2 — `rust-v0.4.2`

Previous published release. Notes are on the releases page.
