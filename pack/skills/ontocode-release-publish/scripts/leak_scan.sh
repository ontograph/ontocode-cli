#!/usr/bin/env bash
# Scan a directory for private paths and internal references before publishing
# to the public distribution repository.
#
# Usage: leak_scan.sh <directory> [extra-pattern ...]
#
# Exit 0 = clean, exit 1 = hits found (classify each before publishing),
# exit 2 = usage or scan error.
set -uo pipefail

target=${1:-}
if [ -z "$target" ] || [ ! -d "$target" ]; then
  echo "usage: leak_scan.sh <directory> [extra-pattern ...]" >&2
  exit 2
fi
shift

# Private org/repo, host paths, local account, internal host octets, and
# internal planning directories. See references/publishing.md.
private_repo='ontograph''-private'
workspace_marker='_''workfolder'
host_path='/opt/''demodb'
local_account='evra''syuk'
internal_host='103''\.228'
planning_dir='[.]''memory-''bank'
pattern="$private_repo|$workspace_marker|$host_path|$local_account|$internal_host|$planning_dir"
for extra in "$@"; do
  pattern="$pattern|$extra"
done

hits=$(grep -rnE "$pattern" --binary-files=without-match --exclude-dir=.git "$target")
grep_status=$?

case "$grep_status" in
  0)
    echo "HITS: classify every line below before publishing"
    echo "$hits"
    exit 1
    ;;
  1)
    echo "CLEAN: no private references in $target"
    exit 0
    ;;
  *)
    echo "ERROR: private-reference scan failed for $target" >&2
    exit 2
    ;;
esac
