# Ontocode Content Pack v8

Content Pack v8 is the independently versioned agents-and-skills release for
the Ontocode CLI. It is published under the `content-pack-v8` tag so content
definitions can be updated without rebuilding the CLI binary.

## Included content

- 25 curated agent definitions
- 28 curated skills
- `pack.toml` provenance and license metadata
- Apache-2.0 `LICENSE` and `NOTICE` files
- manifest entries with archive paths, sizes, SHA-256 digests, provenance,
  licenses, and destination classes
- non-overwriting home and project installers

The pack is built from the reviewed allowlist with `just build-content-pack 8`.
The browsable `pack/` mirror in the distribution repository is extracted from
this same archive.

## Installation

Install into the default Ontocode home directory:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v8 --scope home
```

Install into a project:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v8 --scope project --directory /path/to/project
```

Existing skills and agents are never overwritten by default. The installer
verifies the archive and manifest against `SHA256SUMS` before installation.
