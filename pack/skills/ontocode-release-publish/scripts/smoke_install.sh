#!/usr/bin/env bash
# End-to-end unauthenticated install from a published release.
#
# Proves what local asset checks cannot: that an anonymous user can reach the
# release, download the installer, install the binary, and get the expected
# version. Credentials are stripped so an authenticated token cannot mask a
# private release.
#
# Usage: smoke_install.sh <tag> [expected-version] [asset-name]
#   tag              e.g. rust-v0.4.2.1
#   expected-version e.g. 0.4.2+1  (Cargo form, not the release identity)
#   asset-name       installer asset; defaults to install-ontocode-linux-x64.sh
set -euo pipefail

tag=${1:-}
expected_version=${2:-}
installer_asset=${3:-install-ontocode-linux-x64.sh}
repo=${ONTOCODE_RELEASE_REPO:-ontograph/ontocode-cli}

if [ -z "$tag" ]; then
  echo "usage: smoke_install.sh <tag> [expected-version] [asset-name]" >&2
  exit 2
fi

# The release identity in the tag (0.4.2.1) differs from the Cargo version the
# binary prints (0.4.2+1). Derive the installer's --release input from the tag.
release_id=${tag#rust-v}

smoke_dir=$(mktemp -d) || exit 1
cleanup() { rm -rf "$smoke_dir"; }
trap cleanup EXIT

echo "smoke dir: $smoke_dir"
base="https://github.com/$repo/releases/download/$tag"

env -u GH_TOKEN -u GITHUB_TOKEN curl -fsSL -o "$smoke_dir/inst.sh" \
  "$base/$installer_asset"
sh -n "$smoke_dir/inst.sh"
chmod +x "$smoke_dir/inst.sh"
echo "installer downloaded and syntax-checked"

env -u GH_TOKEN -u GITHUB_TOKEN \
  ONTOCODE_INSTALL_DIR="$smoke_dir/bin" ONTOCODE_HOME="$smoke_dir/home" \
  "$smoke_dir/inst.sh" --release "$release_id" >"$smoke_dir/install.log" 2>&1 ||
  { echo "install FAILED"; tail -20 "$smoke_dir/install.log"; exit 1; }

binary="$smoke_dir/bin/ontocode"
[ -x "$binary" ] || { echo "FAIL: no binary at $binary"; exit 1; }

actual_version=$("$binary" --version 2>&1 | head -1)
echo "installed: $actual_version"

if [ -n "$expected_version" ] && ! printf '%s' "$actual_version" | grep -qF "$expected_version"; then
  echo "FAIL: expected version containing '$expected_version'"
  exit 1
fi

# Compare against the published SHA256SUMS, not a local copy, so a mismatched
# upload is caught.
installed_hash=$(sha256sum "$binary" | cut -d' ' -f1)
if env -u GH_TOKEN -u GITHUB_TOKEN curl -fsSL -o "$smoke_dir/SHA256SUMS" "$base/SHA256SUMS" 2>/dev/null; then
  if grep -qF "$installed_hash" "$smoke_dir/SHA256SUMS"; then
    echo "hash matches published SHA256SUMS"
  else
    echo "FAIL: installed hash $installed_hash absent from published SHA256SUMS"
    exit 1
  fi
else
  echo "FAIL: could not download published SHA256SUMS; hash unverified"
  exit 1
fi

echo "SMOKE PASS: $tag"
