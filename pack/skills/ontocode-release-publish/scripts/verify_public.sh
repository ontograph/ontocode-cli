#!/usr/bin/env bash
# Confirm distribution docs are readable by an anonymous user.
#
# Credentials are stripped: with a token present, a private repo would still
# return 200 and hide the failure.
#
# Usage: verify_public.sh [path ...]   (defaults to the standard doc set)
set -uo pipefail

repo=${ONTOCODE_RELEASE_REPO:-ontograph/ontocode-cli}
base="https://raw.githubusercontent.com/$repo/main"

if [ "$#" -gt 0 ]; then
  paths=("$@")
else
  paths=(README.md CHANGELOG.md LICENSE NOTICE docs/install.md scripts/install/install.sh)
fi

failed=0
for p in "${paths[@]}"; do
  code=$(env -u GH_TOKEN -u GITHUB_TOKEN curl -s -o /dev/null -w '%{http_code}' "$base/$p")
  echo "$code  $p"
  [ "$code" = "200" ] || failed=1
done

if [ "$failed" -ne 0 ]; then
  echo "FAIL: one or more paths are not publicly readable"
  exit 1
fi

echo "All paths publicly readable"
