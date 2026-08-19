# Changelog

Full release notes and downloadable assets are published on the
[Ontocode releases page](https://github.com/ontograph/ontocode-cli/releases).
Per-release notes are also kept under [docs/releases](docs/releases).

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
