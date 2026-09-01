# Ontocode Content Pack v5

Content Pack v5 is an internal development prerelease of the reviewed Ontocode
agent and skill definitions. It is versioned independently from the CLI binary
under the tag `content-pack-v5`.

## Contents

- 25 agent definitions under `agents/`
- 27 skills under `skills/`
- `pack.toml`, `LICENSE`, and `NOTICE`
- a manifest recording every archive path, byte size, SHA-256 digest,
  provenance, license, and destination class

## Installation

Install into the user home:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v5 --scope home
```

Install into a trusted project:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release content-pack-v5 --scope project --directory /path/to/repo
```

Home installs use `$ONTOCODE_HOME/skills` and `$ONTOCODE_HOME/agents`, defaulting
to `~/.ontocode`. Project installs use `.agents/skills` and `.ontocode/agents`.
Existing destinations are refused by default; forced updates create backups.
