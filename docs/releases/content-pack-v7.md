# Ontocode Content Pack v7

Content Pack v7 is the independently versioned agents-and-skills update for
Ontocode CLI 0.4.2.8. It contains 25 agent definitions and 28 reviewed skills
with 81 archive files in total.

The release includes the deterministic archive, manifest, content-pack
installer, and `SHA256SUMS`. The manifest records every archive path, byte size,
SHA-256 digest, provenance, license, and destination class, and is tied to
source commit `5aaa68fd2ca919c70cf4ebf989af4baa8a42dc8f`.

Install into Ontocode home:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v7 --scope home
```

For a trusted project-local installation:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v7 --scope project --directory /path/to/repo
```

The installer verifies the archive against the release `SHA256SUMS` and refuses
to overwrite existing skills or agents.
