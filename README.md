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
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install.sh | sh -s -- --release 0.4.2.3
```

The installer supports Linux x86_64, verifies the binary and project-plan
template against `SHA256SUMS`, and installs to `~/.local/bin` by default.
See [docs/install.md](docs/install.md) for requirements and options.

Install the optional curated build and release-publication skills into Ontocode
home:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release 0.4.2.3 --scope home
```

The content-pack installer also supports trusted project-local installation and
refuses to overwrite existing skills or agents.

## Releases

Release scope:

- unsigned Linux release binary first
- macOS, Windows, and platform npm packages later when needed

Current published release: `0.4.2.3` (`rust-v0.4.2.3`). Its Cargo package and
machine-readable CLI version is `0.4.2+3`, while GitHub release tags, installer
inputs, and asset names use the human release identity `0.4.2.3`.

All releases are listed on the
[releases page](https://github.com/ontograph/ontocode-cli/releases). The
changelog is in [CHANGELOG.md](CHANGELOG.md).
Per-release notes are kept in [docs/releases](docs/releases).

## License

Licensed under the [Apache-2.0 License](LICENSE). See [NOTICE](NOTICE) for
attribution of derived code.