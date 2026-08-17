# Changelog

Full release notes and downloadable assets are published on the
[Ontocode releases page](https://github.com/ontograph/ontocode-cli/releases).
Per-release notes are also kept under [docs/releases](docs/releases).

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
