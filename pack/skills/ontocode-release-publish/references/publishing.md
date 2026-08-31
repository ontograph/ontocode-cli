# Publishing Reference

Detail behind the workflow in `SKILL.md`. Read the section that matches the
current step.

## Contents

- [Leak-scan patterns](#leak-scan-patterns)
- [Classifying a leak-scan hit](#classifying-a-leak-scan-hit)
- [Restaging an asset without importing dirty work](#restaging-an-asset-without-importing-dirty-work)
- [Which docs get published](#which-docs-get-published)
- [Known failure modes](#known-failure-modes)

## Leak-scan patterns

`scripts/leak_scan.sh` searches for six classes of reference. Each exists
because it has appeared in a staged asset at least once.

| Pattern | Catches |
|---|---|
| private source repository names | private source repo named in docs, installers, or clone instructions |
| developer workspace markers | developer working-directory path |
| absolute host paths | machine-specific path |
| local account names | account name in paths and generated output |
| internal host address prefixes | internal host address octets |
| internal planning directory names | internal planning, ADRs, and tracking directories |

Add extra patterns as trailing arguments when a release touches new sensitive
surfaces, for example an internal hostname or a customer name.

## Classifying a leak-scan hit

A hit is not automatically a leak. Classify before acting:

- **Blocking** — host paths, account names, internal addresses, private repo
  URLs in installer or install docs, references to internal planning content.
- **Acceptable** — internal work-item identifiers that carry no location or
  credential, such as `MRF-1.0` in release-notes scope sections. These name a
  change set, not a private resource.

A pattern can also match a name the shipped product genuinely supports. Before
treating such a hit as a leak, check whether product source reads the path as a
caller-supplied or configurable value. If it does, the hit names a documented
convention rather than a private resource; rewriting it would publish
instructions that contradict the binary. Record the decision where the export
is defined instead of relying on judgment at publish time.

One deliberate exception exists in the source repo: `docs/install.md` in the
**source** tree may reference the private clone URL, because that is a source
clone instruction, not distribution. That section is deleted from the
distribution copy rather than rewritten.

## Restaging an asset without importing dirty work

The source checkout normally carries a large volume of unrelated in-progress
edits. Copying a working-tree file straight into a release imports whatever
else is uncommitted in it.

When a staged asset needs a fix, start from the committed version and apply
only the intended change:

```bash
git show HEAD:scripts/install/install.sh > /tmp/base_installer.sh
# apply only the intended edit, then confirm the diff is exactly that edit
diff /tmp/base_installer.sh /tmp/fixed_installer.sh
```

The diff must show only the intended lines. Regenerate `SHA256SUMS` afterward
and re-run `sha256sum -c`.

## Which docs get published

Publish documentation that a release consumer needs:

- release notes per version under `docs/releases/`
- `CHANGELOG.md` with real entries
- `docs/install.md` with a current `--release` example
- `README.md` with install, releases, and license links
- `LICENSE` and `NOTICE`

Do not mirror the source `docs/` tree. Most entries there are 80–180 byte stubs
that redirect to `developers.openai.com`; copying them adds upstream-pointing
noise rather than release documentation. Development-side docs such as
`contributing.md`, `CLA.md`, and internal implementation plans stay in the
private source repo.

`LICENSE` and `NOTICE` are mandatory, not optional. The distribution repo ships
Apache-2.0-derived binaries; publishing them without license text is a
compliance gap.

## Known failure modes

**Installer defaults to the private repo.** The staged installer's `REPO`
default determines the download URL, the release lookup, and `--help` output.
If it points at the private repo, every public install fails. Fix the default
in the source installer so all three derive correctly, rather than patching
one URL.

**Token masks a private release.** `curl` and `gh` pick up `GH_TOKEN` and
`GITHUB_TOKEN` from the environment, so a verification that "passes" may only
prove authenticated access. Always run public checks under
`env -u GH_TOKEN -u GITHUB_TOKEN`.

**Version mismatch that is not a bug.** The binary prints the Cargo version
(`0.4.2+1`) while the tag and assets use the release identity (`0.4.2.1`).
Check which form the surface should use before investigating.

**Stale version pin in install docs.** `docs/install.md` in the distribution
repo carries a `--release` example that silently goes stale after each release.
Update it as part of publishing.

**Docs describe a stale pack.** `README.md` and `CHANGELOG.md` describe what a
content pack contains and which release to install. Both go stale when the pack
is re-cut. Verify the documented command end to end, rather than assuming a
documented version still resolves.

**Large asset upload times out.** Uploading a multi-hundred-megabyte binary can
exceed a command timeout after GitHub has already created the release as a
draft and accepted the smaller assets. Inspect the release before retrying:
re-running the create command duplicates work, while `gh release upload` adds
only the missing asset. Publish the draft afterward.

**`gh` lacks `release edit`.** Older `gh` builds cannot flip a draft. Patch the
release through the API instead of recreating it.

**Release verification uses a stale expectation.** A release-gate script that
hard-codes expected metadata fails when the source it checks is updated
legitimately. Compare the script against current source before assuming the
artifact is wrong; the checker is often what drifted.

**Whole-worktree verification reports unrelated symbols.** This repo carries
in-progress edits, so a repository-wide diff check can fail on files the current
task never touched. Scope verification to the intended files and leave the rest
alone.

**Distribution clone has no git identity.** A fresh clone may lack
`user.name`/`user.email`, which blocks annotated tags and commits. Set them
locally on that clone.

**Local `main` cannot fast-forward.** When dirty files overlap incoming
commits, git refuses the update. That refusal is correct — leave it alone
rather than forcing, and do not discard the user's work to make it advance.
