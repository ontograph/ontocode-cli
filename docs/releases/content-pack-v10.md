# Ontocode Content Pack v10

Content Pack v10 is the independently versioned agents-and-skills release for
the Ontocode CLI. It is published under the `content-pack-v10` tag so content
definitions can be updated without rebuilding the CLI binary.

## Included content

- 20 curated agent definitions
- 27 curated skills
- `pack.toml` provenance and license metadata
- Apache-2.0 `LICENSE` and `NOTICE` files
- a manifest with archive paths, sizes, SHA-256 digests, provenance, licenses,
  and destination classes
- a non-overwriting home/project installer

The browsable `pack/` mirror in this repository is extracted from the same
archive uploaded to the release.

## Installation

Install into the default Ontocode home directory:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v10 --scope home
```

Install into a trusted project:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v10 --scope project --directory /path/to/project
```

The installer verifies the archive against `SHA256SUMS` and refuses to
overwrite existing skills or agents.

## Changes since v9

- Removes the four librarian agents (`librarian`, `librarian-manager`, `librarian-reviewer`, `librarian-worker`).
- Removes the `ontocode-ontograph-km` skill; Knowledge Modules are retired.
- Drops librarian references from the remaining skills and templates.
