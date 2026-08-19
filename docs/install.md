## Installing

### System requirements

| Requirement                 | Details                                                         |
| --------------------------- | --------------------------------------------------------------- |
| Operating systems           | macOS 12+, Ubuntu 20.04+/Debian 10+, or Windows 11 **via WSL2** |
| Git (optional, recommended) | 2.23+ for built-in PR helpers                                   |
| RAM                         | 4-GB minimum (8-GB recommended)                                 |

### Install the release

The published installer supports Linux x86_64 and verifies the release binary
and project-plan template against `SHA256SUMS`:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install.sh | sh
```

Pin an explicit release with `--release`, for example `--release 0.4.2.4`.

Release identity note: GitHub tags, installer inputs, and asset names use the
human release identity such as `0.4.2.4`, while the CLI reports the
machine-readable Cargo version such as `0.4.2+4`.

### Install the optional content pack

Release `0.4.2.4` includes a curated pack containing the repository-owned build
and release-publication skills. Install it into Ontocode home with:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release 0.4.2.4 --scope home
```

For a trusted project-local installation, use:

```bash
curl -fsSL https://raw.githubusercontent.com/ontograph/ontocode-cli/main/scripts/install/install-content-pack.sh | sh -s -- --release 0.4.2.4 --scope project --directory /path/to/repo
```

The installer verifies the archive against the release `SHA256SUMS` and refuses
to overwrite existing skills or agents.

### Verifying a download

Every release publishes `SHA256SUMS`. To verify assets manually, download them
alongside `SHA256SUMS` and run:

```bash
sha256sum -c SHA256SUMS
```

## Tracing / verbose logging

Ontocode is written in Rust, so it honors the `RUST_LOG` environment variable to configure its logging behavior.

The TUI records diagnostics in bounded local stores by default. Set `log_dir` explicitly to enable a plaintext TUI log for a run:

```bash
ontocode -c log_dir=./.ontocode-log
tail -F ./.ontocode-log/ontocode-tui.log
```

The non-interactive mode (`ontocode exec`) defaults to `RUST_LOG=error`, but messages are printed inline, so there is no need to monitor a separate file.

See the Rust documentation on [`RUST_LOG`](https://docs.rs/env_logger/latest/env_logger/#enabling-logging) for more information on the configuration options.
