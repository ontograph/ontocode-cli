#!/bin/sh

set -eu

REPO="${ONTOCODE_RELEASE_REPO:-ontograph/ontocode-cli}"
RELEASE="${ONTOCODE_RELEASE:-}"
SCOPE="home"
PROJECT_DIR=""

usage() {
  cat <<EOF
Usage: install-content-pack.sh [--release VERSION] [--scope home|project] [--directory PATH]

Project scope requires --directory. Existing skill or agent destinations are
never overwritten.

VERSION may be a CLI release such as 0.4.2.4, or a content-pack release such
as content-pack-v1. Omit --release to install the newest content pack.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --release) [ "$#" -ge 2 ] || exit 2; RELEASE="$2"; shift ;;
    --scope) [ "$#" -ge 2 ] || exit 2; SCOPE="$2"; shift ;;
    --directory) [ "$#" -ge 2 ] || exit 2; PROJECT_DIR="$2"; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

case "$SCOPE" in
  home) skills_root="${ONTOCODE_HOME:-$HOME/.ontocode}/skills"; agents_root="${ONTOCODE_HOME:-$HOME/.ontocode}/agents" ;;
  project)
    [ -n "$PROJECT_DIR" ] || { echo "Project scope requires --directory." >&2; exit 2; }
    skills_root="$PROJECT_DIR/.agents/skills"
    agents_root="$PROJECT_DIR/.ontocode/agents"
    ;;
  *) echo "Scope must be home or project." >&2; exit 2 ;;
esac

for command_name in curl tar sha256sum awk mktemp install cp mkdir basename sed head; do
  command -v "$command_name" >/dev/null 2>&1 || { echo "$command_name is required." >&2; exit 1; }
done

normalize_version() {
  case "$1" in rust-v*) printf '%s\n' "${1#rust-v}" ;; v*) printf '%s\n' "${1#v}" ;; *) printf '%s\n' "$1" ;; esac
}

# Content packs ship under their own tag so they can be updated without
# rebuilding the CLI. Only fall back to a CLI release tag when the caller
# names a CLI version.
resolve_tag() {
  case "$1" in
    content-pack-*) printf '%s\n' "$1" ;;
    *) printf 'rust-v%s\n' "$(normalize_version "$1")" ;;
  esac
}

if [ -z "$RELEASE" ] || [ "$RELEASE" = "latest" ]; then
  tag="$(curl -fsSL "https://api.github.com/repos/$REPO/releases?per_page=100" \
    | sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' \
    | grep '^content-pack-' \
    | head -n 1)"
  [ -n "$tag" ] || { echo "No content-pack release found in $REPO." >&2; exit 1; }
else
  tag="$(resolve_tag "$RELEASE")"
fi
case "$tag" in
  content-pack-*) version="${tag#content-pack-v}" ;;
  *) version="$(normalize_version "$tag")" ;;
esac
archive_name="ontocode-content-pack-$version.tar.gz"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT INT TERM
archive="$tmp_dir/$archive_name"
checksums="$tmp_dir/SHA256SUMS"
base_url="${ONTOCODE_RELEASE_BASE_URL:-https://github.com/$REPO/releases/download/$tag}"
curl -fL# "$base_url/$archive_name" -o "$archive"
curl -fL# "$base_url/SHA256SUMS" -o "$checksums"
expected="$(awk -v asset="$archive_name" '$2 == asset { print $1; exit }' "$checksums")"
[ -n "$expected" ] || { echo "SHA256SUMS does not list $archive_name." >&2; exit 1; }
actual="$(sha256sum "$archive" | awk '{print $1}')"
[ "$actual" = "$expected" ] || { echo "Content-pack checksum mismatch." >&2; exit 1; }

tar -tzf "$archive" | while IFS= read -r entry; do
  case "$entry" in content-pack/*) ;; *) echo "Unsafe archive path: $entry" >&2; exit 1 ;; esac
  case "$entry" in *'/../'*|../*|*/..|/*) echo "Unsafe archive path: $entry" >&2; exit 1 ;; esac
done
if tar -tvzf "$archive" | awk '$1 !~ /^[d-]/ { exit 1 }'; then :; else
  echo "Content pack contains unsupported file types." >&2
  exit 1
fi

tar -xzf "$archive" -C "$tmp_dir"
pack_root="$tmp_dir/content-pack"
[ -f "$pack_root/pack.toml" ] || { echo "Content pack is missing pack.toml." >&2; exit 1; }

if [ -d "$pack_root/skills" ]; then
  for source_dir in "$pack_root"/skills/*; do
    [ -d "$source_dir" ] || continue
    name="$(basename "$source_dir")"
    [ -f "$source_dir/SKILL.md" ] || { echo "Skill $name is missing SKILL.md." >&2; exit 1; }
    [ ! -e "$skills_root/$name" ] || { echo "Refusing to overwrite $skills_root/$name" >&2; exit 1; }
  done
fi
if [ -d "$pack_root/agents" ]; then
  for source_file in "$pack_root"/agents/*.toml; do
    [ -f "$source_file" ] || continue
    name="$(basename "$source_file")"
    [ ! -e "$agents_root/$name" ] || { echo "Refusing to overwrite $agents_root/$name" >&2; exit 1; }
  done
fi

mkdir -p "$skills_root" "$agents_root"
if [ -d "$pack_root/skills" ]; then
  for source_dir in "$pack_root"/skills/*; do
    [ -d "$source_dir" ] || continue
    cp -R "$source_dir" "$skills_root/"
  done
fi
if [ -d "$pack_root/agents" ]; then
  for source_file in "$pack_root"/agents/*.toml; do
    [ -f "$source_file" ] || continue
    install -m 0644 "$source_file" "$agents_root/$(basename "$source_file")"
  done
fi

echo "Ontocode content pack $version installed for $SCOPE scope."
