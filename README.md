# Ontocode CLI

Ontocode CLI is an independent fork of the Codex CLI codebase. This repository
is its distribution point: release notes, binaries, installers, and checksums
are published here. It is not an official OpenAI, Azure, ChatGPT, npm,
Homebrew, or IDE distribution.

The canonical binary is `ontocode`.

## Install

Install the current Linux x64 release:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install.sh | sh
```

Pin an explicit release:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install.sh | sh -s -- --release 0.4.2.4
```

The installer supports Linux x86_64, verifies the binary and project-plan
template against `SHA256SUMS`, and installs to `~/.local/bin` by default.
See [docs/install.md](docs/install.md) for requirements and options.

## Agents and skills

The agent definitions and skills ship as a content pack, released separately
from the CLI so they can be updated without reinstalling the binary. The
current pack is `content-pack-v1` and contains 27 agents and 47 skills.

Install into Ontocode home:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --scope home
```

Install into a single project:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --scope project --directory /path/to/project
```

Without `--release` the installer selects the newest content pack. Pass
`--release content-pack-v1` to pin one.

Home installs land in `$ONTOCODE_HOME/skills` and `$ONTOCODE_HOME/agents`,
defaulting to `~/.ontocode`. Project installs land in `.agents/skills` and
`.ontocode/agents`. The installer verifies the archive against `SHA256SUMS` and
refuses to overwrite an existing skill or agent.

## Releases

Release scope:

- unsigned Linux release binary first
- macOS, Windows, and platform npm packages later when needed

Current internal development prerelease: `0.4.2.4` (`rust-v0.4.2.4`). Its Cargo
package and machine-readable CLI version is `0.4.2+4`, while GitHub release
tags, installer inputs, and asset names use the human release identity
`0.4.2.4`.

All releases are listed on the
[releases page](https://github.com/ontograph/ontocode-cli/releases). The
changelog is in [CHANGELOG.md](CHANGELOG.md).
Per-release notes are kept in [docs/releases](docs/releases).
See the [0.4.2.4 release notes](docs/releases/v0.4.2.4.md).

Content packs are versioned independently of the CLI and use `content-pack-v*`
tags.

## License

Licensed under the [Apache-2.0 License](LICENSE). See [NOTICE](NOTICE) for
attribution of derived code.