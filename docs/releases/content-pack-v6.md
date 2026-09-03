# Ontocode Content Pack v6

Content Pack v6 is the independently versioned agents-and-skills update for
Ontocode CLI 0.4.2.7. It contains 25 agent definitions and 27 skills built from
the reviewed public allowlist.

The release includes the archive, manifest, content-pack installer, and
`SHA256SUMS`. The manifest records every archive path, byte size, SHA-256 digest,
provenance, license, and destination class.

Install into Ontocode home:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v6 --scope home
```

For a trusted project-local installation:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v6 --scope project --directory /path/to/repo
```

The installer verifies the archive against the release `SHA256SUMS` and refuses
to overwrite existing skills or agents.
