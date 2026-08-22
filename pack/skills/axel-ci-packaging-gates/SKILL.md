---
name: axel-ci-packaging-gates
description: Use when changes touch .github/workflows, debian, docker, kubernetes, snap, release documentation, repository-wide quality-gate wiring, or claims about Axel security, supply-chain, packaging, and release gates.
license: MPL-2.0
metadata:
  owner: axel
  version: "1.0.0"
  scope: gate/packaging wiring; product implementation belongs to domain owners
---

# Axel CI Packaging Gates

## Gate Map

- Path-selected checks live in `scripts/select-gates.sh`. Use it before hand-
  assembling a command list.
- Spreadsheet quality gates include required-check contracts, cargo-deny/
  cargo-audit, browser/Mocha tests, Playwright/UI assurance, native-grid
  performance, clang-tidy, and hardening jobs. See
  `.github/workflows/spreadsheet-quality-gates.yml`.
- Security scanning includes CodeQL and nightly hardening. Supply-chain findings
  need affected-version and upgrade-path evidence.
- Packaging surfaces are split: `docker/`, `debian/`, `snap/`, and
  `kubernetes/helm/axel`. Change the surface named by the task; do not normalize
  them into a shared abstraction.

## Workflow

1. Identify whether the change edits a gate, adds a check to an existing job, or
   changes a packaged artifact.
2. Reuse an existing workflow/job when the trigger and artifact match. Do not
   add a parallel gate for a problem one matrix already owns.
3. Make required/failure policy explicit. A new advisory check should be
   enforced or clearly nightly-only, not accidentally advisory forever.
4. For packaging, verify installed paths, service definitions, secrets, entry
   points, versions, architectures, and startup behavior against the actual
   manifest.

## Artifact And Gate Identity

Create a fresh directory for nontrivial packaging or release investigation. Do
not reuse prior logs, images, packages, or reports as evidence. Before drawing a
verdict, record:

```text
source=<repository/worktree and committed SHA>
gate=<workflow/job or script and exit status>
target=<package/image/helm chart identity>
digest=<artifact/package digest>
command=<exact command>
policy=<required|advisory|nightly-only>
```

If a required gate cannot run, report the blocker and leave closure open. Do not
substitute a weaker local check, mark it advisory, or infer CI success from a
different branch, dirty tree, cache, or artifact age.

## Validation

Start with the repository selector:

```sh
scripts/select-gates.sh --staged --run
```

Validate required-check wiring:

```sh
python3 scripts/check-required-checks-contract.py
```

Run packaging builds only for the touched target. Record image/package ID,
source SHA/worktree, command, and artifact digest. Do not claim release parity
from a different branch, dirty tree, or cache-only build.

## Routing

- Formal release qualification: `$axel-release-qualification`
- Playwright gate failures: `$axel-debug-playwright-reports`
- Rust supply-chain details: `$axel-rust-supplement`
