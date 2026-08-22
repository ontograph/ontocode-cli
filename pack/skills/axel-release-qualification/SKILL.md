---
name: axel-release-qualification
description: Qualify Axel direct Qt desktop artifacts as GA, prerelease, or not releasable using source provenance, baseline build, ABI, package, extracted-runtime, native-grid, and checksum evidence. Use when preparing or reviewing an Axel release candidate, deciding GA versus prerelease, or checking whether package evidence permits publication. Never use it as implicit authorization to publish.
---

# Axel Release Qualification

Produce an evidence-backed release verdict. Do not publish unless the user explicitly requests publication in the current conversation.

## Workflow

1. Record the candidate source commit and artifact paths. Reject evidence from a different source SHA or rebuilt bytes.
2. Determine required gates from the repository release rules and owning tracker. Preserve any `HOLD`, `PARTIAL`, or `FAIL`; missing evidence is not a pass.
3. Verify the mandatory direct Qt baseline:
   - LibreOffice and non-Qt native runtime built on Ubuntu 22.04.
   - `coda-qt` and Qt collection built with Debian 12 Qt 6.4.2.
   - Ubuntu 22.04 compatibility libraries supplied through `CODA_QT_BASELINE_LIB_DIR` without bundling glibc-owned libraries.
4. Verify source provenance with `scripts/stamp-provisioned-artifact-sha.sh` and `scripts/check-provisioned-artifact-sha.sh`. The release tag must target the exact provisioned SHA.
5. Package only with `scripts/package-direct-webhost-tarball.sh`, then run `scripts/check-direct-webhost-package-runtime.sh` against the packaged directory.
6. Require the ABI gate to scan every packaged ELF, reject requirements newer than `GLIBC_2.35`, reject `GLIBC_ABI_DT_RELR`, reject unresolved non-glibc dependencies, and confirm the real `QtWebEngineProcess` ELF.
7. Extract the exact final tarball into a fresh directory and run its bundled `run.sh` in Ubuntu 22.04 with isolated writable HOME/XDG directories and inherited Qt/library paths unset.
8. Require runtime evidence for native-grid composite active, browser grid retired, a visible nonblank QWidget spreadsheet surface, and one clean document release. Any fallback, `surface=QWebEngineView`, missing dependency/resource, blank capture, or `result=fail` blocks qualification.
9. Generate and verify SHA-256 checksums for every binary asset. Any restamp or rebuild invalidates prior ABI, checksum, extraction, and runtime evidence.
10. Return one verdict:
   - `GA`: every required gate passes for the exact immutable bytes.
   - `PRERELEASE`: artifact is usable but a required qualification gate remains `HOLD`, `PARTIAL`, or explicitly accepted as incomplete.
   - `NOT RELEASABLE`: runtime, ABI, provenance, integrity, or mandatory packaging evidence fails or is missing.

## Publication Guard

- Qualification does not authorize tagging, pushing, uploading, release creation, or Snap/Snapcraft operations.
- Publish only after an explicit current-conversation request and only at the qualified level.
- Never move a published tag or replace an uploaded asset under the same tag. Fix the owner and publish a new patch tag.

## Evidence

Report the verdict, source SHA, artifact names and sizes, checksums, each gate command with exit status, captured runtime artifact paths, unresolved gaps, and the highest publication level supported. Distinguish observed evidence from pending commands.
