#!/bin/sh
# Install checked standalone okms binaries without Python or a source checkout.
set -eu

fail() { printf '%s\n' "$*" >&2; exit 1; }
usage() {
    cat <<'USAGE'
Usage: sh install.sh [--version X.Y.Z] [--bin-dir DIR] [--project DIR]
                     [--docs RELATIVE_PATH] [--dry-run] [--release-dir DIR]
Install the latest regular GitHub release into $HOME/.local/bin.
--project also initializes its embedded Hybrid Team payload.
--dry-run verifies assets and preflights setup without writes.
--release-dir uses checked local assets without network access.
USAGE
}

version=
release_dir=
project=
docs=
dry_run=false
bin_dir=${HOME:?HOME must be set}/.local/bin
while [ "$#" -gt 0 ]; do
    case "$1" in
        --version|--release-dir|--project|--docs|--bin-dir)
            [ "$#" -ge 2 ] && [ -n "$2" ] || fail "Missing value for $1"
            case "$1" in
                --version) version=$2 ;;
                --release-dir) release_dir=$2 ;;
                --project) project=$2 ;;
                --docs) docs=$2 ;;
                --bin-dir) bin_dir=$2 ;;
            esac
            shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        --help|-h) usage; exit 0 ;;
        *) fail "Unknown argument: $1" ;;
    esac
done
[ -z "$docs" ] || [ -n "$project" ] || fail "--docs requires --project"
if [ -n "$version" ]; then
    printf '%s\n' "$version" | awk '/^[0-9]+\.[0-9]+\.[0-9]+$/ {ok=1} END {exit !ok}' ||
        fail "Version must be X.Y.Z"
fi

case "$(uname -s)" in Linux) os=unknown-linux-musl ;; Darwin) os=apple-darwin ;; *) fail "Supported platforms: Linux/WSL and macOS" ;; esac
case "$(uname -m)" in x86_64|amd64) arch=x86_64 ;; arm64|aarch64) arch=aarch64 ;; *) fail "Supported architectures: x86_64 and arm64" ;; esac
archive=okms-$arch-$os.tar.gz
command -v tar >/dev/null 2>&1 || fail "tar is required"
if command -v sha256sum >/dev/null 2>&1; then
    checksum() { sha256sum "$1" | awk '{print $1}'; }
elif command -v shasum >/dev/null 2>&1; then
    checksum() { shasum -a 256 "$1" | awk '{print $1}'; }
else
    fail "sha256sum or shasum is required"
fi
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT HUP INT TERM
if [ -n "$release_dir" ]; then
    cp "$release_dir/SHA256SUMS" "$work/SHA256SUMS"
    cp "$release_dir/$archive" "$work/$archive"
else
    command -v curl >/dev/null 2>&1 || fail "curl is required for downloads"
    base=https://github.com/tidusvn05/okms/releases/latest/download
    [ -z "$version" ] || base=https://github.com/tidusvn05/okms/releases/download/hybrid-team-v$version
    for asset in SHA256SUMS "$archive"; do
        curl --fail --location --silent --show-error --proto '=https' --proto-redir '=https' \
            --retry 2 --connect-timeout 15 --max-time 180 --max-filesize 104857600 \
            "$base/$asset" --output "$work/$asset"
    done
fi
[ "$(wc -c < "$work/$archive")" -le 104857600 ] || fail "Archive exceeds 100 MiB"
expected=$(awk -v name="$archive" '
    NF != 2 || length($1) != 64 || $1 ~ /[^0-9a-f]/ {bad=1}
    $2 == name {count++; digest=$1}
    END {if (bad || count != 1) exit 1; print digest}
' "$work/SHA256SUMS") || fail "Invalid or missing archive checksum"
[ "$(checksum "$work/$archive")" = "$expected" ] || fail "Archive checksum mismatch"

tar -tzf "$work/$archive" > "$work/members"
awk '
    $0 != "okms" && $0 != "LICENSE-MIT" && $0 != "LICENSE-APACHE" {bad=1}
    {seen[$0]++; total++}
    END {exit (bad || total != 3 || seen["okms"] != 1 ||
        seen["LICENSE-MIT"] != 1 || seen["LICENSE-APACHE"] != 1)}
' "$work/members" || fail "Archive must contain only okms and both licenses"
tar -tvzf "$work/$archive" > "$work/types"
awk 'substr($0, 1, 1) != "-" {bad=1} END {exit bad}' "$work/types" ||
    fail "Archive links and special files are forbidden"
mkdir "$work/extracted"
tar -xzf "$work/$archive" -C "$work/extracted"
chmod 755 "$work/extracted/okms"
observed=$("$work/extracted/okms" --version)
installed_version=$(printf '%s\n' "$observed" | awk '
    NF == 2 && $1 == "okms" && $2 ~ /^[0-9]+\.[0-9]+\.[0-9]+$/ {value=$2}
    END {if (!value) exit 1; print value}
') || fail "Invalid okms binary version"
[ -z "$version" ] || [ "$version" = "$installed_version" ] || fail "Binary version does not match pin"

set -- "$work/extracted/okms" init
[ -z "$project" ] || set -- "$@" --project "$project"
[ -z "$docs" ] || set -- "$@" --docs "$docs"
if [ -n "$project" ]; then
    "$@" --dry-run > "$work/preflight.json"
fi
if [ -e "$bin_dir/okms" ] || [ -L "$bin_dir/okms" ]; then
    [ -f "$bin_dir/okms" ] && [ ! -L "$bin_dir/okms" ] || fail "Existing CLI must be a regular file"
    existing=$("$bin_dir/okms" --version 2>/dev/null) || fail "Existing okms path is not a working CLI"
    case "$existing" in "okms "*) ;; *) fail "Existing okms path belongs to another program" ;; esac
fi
if [ "$dry_run" = true ]; then
    printf 'Verified okms %s (%s); target: %s/okms\n' "$installed_version" "$arch-$os" "$bin_dir"
    [ -z "$project" ] || cat "$work/preflight.json"
    exit 0
fi
if [ -n "$project" ]; then "$@"; fi
mkdir -p "$bin_dir"
cli_temp=$(mktemp "$bin_dir/.okms-install.XXXXXX")
cp "$work/extracted/okms" "$cli_temp"
chmod 755 "$cli_temp"
mv -f "$cli_temp" "$bin_dir/okms"
printf 'Installed okms %s at %s/okms\n' "$installed_version" "$bin_dir"
