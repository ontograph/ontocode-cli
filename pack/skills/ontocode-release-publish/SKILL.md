---
name: ontocode-release-publish
description: Publish an Ontocode release and its release documentation to the public distribution repository `ontograph/ontocode-cli`. Use when asked to publish or ship a release, create a GitHub release, upload release assets or binaries, publish release notes or release docs, cut a version such as 0.4.2.1, or verify that a published release installs correctly. Covers asset verification, public-leak scrubbing, release creation, docs publication, and the unauthenticated installer smoke.
---

# Ontocode Release Publish

Publish release artifacts and documentation to the public distribution
repository. Building the binary and the one-line release policy are owned by
`.ontocode/skills/ontocode-build/SKILL.md`; read it before forming any build or
packaging command. This skill starts once release assets exist.

## Distribution Policy

Publish release documentation and binaries only to
`https://github.com/ontograph/ontocode-cli`. It is the single distribution
location for release notes, the `ontocode` binary, installers, the project-plan
template, and `SHA256SUMS`. Do not publish releases or upload release assets to
any other repository. Source development stays in the private source
repository; only published release artifacts go to the distribution repository.

That repository is public, so treat every published asset as world-readable.
Confirm release notes and artifacts carry no private paths, internal hostnames,
tokens, or unreleased planning detail before uploading.

Agents and skills are published there in two forms built from one artifact:

- Versioned content-pack archives attached to `content-pack-v<n>` releases are
  the integrity and versioning authority for agents and skills.
- A browsable `pack/` directory in the distribution checkout
  (`pack/pack.toml`, `pack/skills/<name>/SKILL.md`, `pack/agents/<name>.toml`)
  mirrors the newest published pack. The publish pipeline writes it from the
  same built staging pack that produced the release archive; never edit `pack/`
  by hand and never populate it from the private working tree.

Private-fork releases must not depend on OpenAI release workflows, runner
labels, Azure signing, npm trusted publishing, winget, or dev-site deploys. Use
GitHub-hosted runners and unsigned artifacts unless the fork owns the
platform-specific infrastructure.

Push source commits and tags to the development remote, then create the release
against the distribution repository.

| Repository | Role | Visibility |
|---|---|---|
| development remote (`ontograph` remote) | source, tags, evidence commits | private |
| `ontograph/ontocode-cli` | distribution only: release notes, binary, installers, `SHA256SUMS`, docs, browsable content-pack mirror | **public** |

## Release Identity

Two version strings coexist and are not interchangeable. For a fix release
whose human identity is `<base>.<revision>`:

- human release identity `<base>.<revision>` — GitHub tag
  (`rust-v<base>.<revision>`), installer `--release` input, asset names
- Cargo/machine version `<base>+<revision>` — what `ontocode --version` prints

For example, release `0.4.2.2` maps to Cargo version `0.4.2+2`.

Expect the smoke test to print the `+`-form. A mismatch between the two forms is
the most common false alarm; confirm which form a surface is supposed to use
before treating a difference as a defect.

## Release Kinds

Two kinds of release are published here, and they version independently.

| Kind | Tag | Carries |
|---|---|---|
| CLI release | `rust-v<version>` | binary, installers, template, checksums |
| content pack | `content-pack-v<n>` | agents and skills archive, manifest, its installer, `pack/` mirror sync |

A change to agents or skills alone ships as a content-pack release. Do not
rebuild the binary or bump the CLI version for it, and never mutate an already
published release to carry new content.

When a release changes an installer, publish that installer as a release asset
**and** update the copy in the distribution repo. `README.md` tells users to
pipe the installer from the `main` branch, so a stale branch copy makes newly
documented commands fail even though the release itself is correct. Confirm the
two are byte-identical before pushing.

## Workflow

Run these in order. Do not skip step 2; the target repository is public.

### 1. Verify assets

Confirm the tag exists on the distribution repo and the release does not:

```bash
gh release view <tag> --repo ontograph/ontocode-cli --json tagName,assets
git ls-remote --tags https://github.com/ontograph/ontocode-cli
```

Then verify every asset hash in the staging directory:

```bash
cd <release-assets-dir> && sha256sum -c SHA256SUMS
```

All entries must report `OK`. `SHA256SUMS` must cover every asset that will be
uploaded.

### 2. Scrub for private references

Every uploaded asset and every file in the distribution repo is world-readable.
Run `scripts/leak_scan.sh` against both the asset directory and the distribution
checkout; see [references/publishing.md](references/publishing.md) for what the
patterns mean and which hits are acceptable.

Treat any hit as blocking until classified. Do not upload while a hit is
unexplained.

### 3. Confirm the installer points at the public repo

The installer's `REPO` default decides where end users download from. A staged
installer that still defaults to the private repo produces a release nobody can
install:

```bash
grep -n 'REPO=' <release-assets-dir>/install-ontocode-linux-x64.sh
```

It must resolve to `ontograph/ontocode-cli`. If it does not, fix the source
installer's default rather than patching the asset in place, then restage. See
[references/publishing.md](references/publishing.md) for the restaging rule that
keeps unrelated dirty work out of the release.

### 4. Create the release

```bash
cd <release-assets-dir>
gh release create <tag> --repo ontograph/ontocode-cli \
  --title "<title>" \
  --notes-file <release-notes.md> \
  --prerelease \
  <asset> [<asset>...]
```

Use `--prerelease` for internal or development release candidates. Upload
`SHA256SUMS` as an asset alongside the files it covers. Never move or overwrite
an existing tag.

Verify the upload landed completely:

```bash
gh release view <tag> --repo ontograph/ontocode-cli \
  --json tagName,isPrerelease,assets \
  --jq '{tag:.tagName,pre:.isPrerelease,assets:[.assets[]|{name,size}]}'
```

Check the asset count and sizes against the staging directory.

### 5. Publish the release docs

Release documentation belongs in the distribution repo, not only in the release
body. Update in the distribution checkout:

- `docs/releases/v<version>.md` — a copy of the release notes, versioned in-repo
- `CHANGELOG.md` — a real entry per release, not a bare redirect link
- `docs/install.md` — the `--release` example must name the current version
- `README.md` — links to release notes and license
- `LICENSE` and `NOTICE` — required; the repo distributes Apache-2.0 binaries

Do not mirror the whole source `docs/` tree. Most files there are short stubs
redirecting to upstream OpenAI docs, and development-side docs such as
contributing and CLA guides stay private. See
[references/publishing.md](references/publishing.md) for the selection rule.

Re-run the leak scan, then commit and push.

### 6. Smoke test the live release

The only meaningful proof is an unauthenticated install from the published
release, not from local files:

```bash
scripts/smoke_install.sh <tag> [expected-version]
```

It downloads the installer over plain HTTPS with credentials stripped, installs
into a temporary directory with `ONTOCODE_INSTALL_DIR` and `ONTOCODE_HOME`
overridden, prints the version, compares the installed binary hash to the
published `SHA256SUMS`, and removes the temporary directory. Read the script
before running it if the release layout differs.

Finally confirm the docs are publicly readable:

```bash
scripts/verify_public.sh
```

### 7. Content-pack releases

A content-pack release follows the same six steps with a narrower asset set:
the archive, its manifest, the content-pack installer, release notes, and
`SHA256SUMS`. Build the pack with `just build-content-pack`; do not assemble it
by hand.

```bash
gh release create content-pack-v<n> --repo ontograph/ontocode-cli \
  --title "Ontocode Content Pack v<n>" \
  --notes-file <release-notes.md> \
  --prerelease \
  <archive> <manifest> <installer> <release-notes.md> SHA256SUMS
```

The smoke test for a content pack is an anonymous install from the published
release into temporary home and project roots, plus a second install that must
be refused. Also verify that omitting `--release` resolves the newest content
pack, since that is the documented default path.

After the release is live, sync the browsable mirror from the same staging
directory that produced the archive: replace `pack/` in the distribution
checkout with the staging pack contents, confirm the tree is byte-identical to
the archive contents, re-run the leak scan, then commit and push to `main`.
Leave `pack/` untouched when a release ships no content change. A `pack/` tree
that differs from the newest published pack archive is a release defect; repair
it by republishing from the built artifact, never by editing mirror files in
place.

## Constraints

- Never strip credentials by assumption — use `env -u GH_TOKEN -u GITHUB_TOKEN`
  so the check proves anonymous access rather than authenticated access.
- Preserve unrelated dirty files in the source checkout. This repository
  routinely carries hundreds of in-progress edits; do not stash, revert, or
  sweep them into a release commit.
- Do not remove release worktrees or distribution clones without explicit
  authorization. Removing `/tmp` scratch files created during the run is fine.
- A distribution clone may need local `git config user.name` and `user.email`
  before annotated tags or commits succeed.

## Resources

- `scripts/leak_scan.sh` — scan a directory for private paths and internal references
- `scripts/smoke_install.sh` — end-to-end unauthenticated install from a published release
- `scripts/verify_public.sh` — confirm distribution docs return HTTP 200 anonymously
- [references/publishing.md](references/publishing.md) — leak-pattern meanings, docs selection rule, asset restaging, and failure modes
