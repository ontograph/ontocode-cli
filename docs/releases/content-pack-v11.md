# Ontocode Content Pack v11

Content Pack v11 is the independently versioned agents-and-skills release for the Ontocode CLI. It replaces v10 without a CLI rebuild.

## Changes since v10

- `ontocode-memory-bank` no longer names a maintainer's home directory. It now points at `$ONTOCODE_HOME/skills/.system/ontocode-memory-bank/SKILL.md` and the plan template under `$ONTOCODE_HOME/templates/`.
- The pack builder and `ontocode-release-publish/scripts/leak_scan.sh` now reject absolute home-directory and data-root paths, so that class of leak blocks the build.
- `council-manager`, `council-panelist` and `council-consolidator` add a design-review profile with comprehension, feasibility and simplicity seats; `md-plans-manager` runs a comprehension review between validator and challenger.
- `ontocode-docs` states what documentation should and should not cover and how to bring docs back in sync with code.
- `ontocode-release-publish` materializes the plan template from the shipped asset.
- The `personas` coordinator prompts tell workers to extend existing code inside their write set and report problems outside it.

## Included content

- 20 curated agent definitions
- 27 curated skills
- `pack.toml` provenance and license metadata
- Apache-2.0 `LICENSE` and `NOTICE` files
- a manifest with archive paths, sizes, SHA-256 digests, provenance, licenses, and destination classes
- a non-overwriting home/project installer

The browsable `pack/` mirror in this repository is extracted from the same archive uploaded to the release.

## Installation

Install into the default Ontocode home directory:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v11 --scope home
```

Install into a trusted project:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v11 --scope project --directory /path/to/project
```

The installer verifies the archive against `SHA256SUMS` and refuses to overwrite existing skills or agents.
