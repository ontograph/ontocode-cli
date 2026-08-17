[CmdletBinding()]
param(
    [string]$Release = $env:ONTOCODE_RELEASE
)

$ErrorActionPreference = "Stop"

Write-Error @"
Ontocode private alpha does not publish a Windows installer yet.

Build locally from the repository root instead:
  cd ontocode-rs
  `$env:CARGO_BUILD_JOBS = "8"
  cargo build --release -p ontocode-cli --bin ontocode

Expected binary:
  ontocode-rs\target\release\ontocode.exe
"@
